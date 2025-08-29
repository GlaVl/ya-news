from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_comment_data):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_comment_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(not_author_client, news, form_comment_data,
                                 not_author
                                 ):
    url = reverse('news:detail', args=(news.id,))
    response = not_author_client.post(url, data=form_comment_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_comment_data['text']
    assert comment.author == not_author


def test_user_cant_use_bad_words(not_author_client, news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    # Отправляем запрос через авторизованный клиент.
    url = reverse('news:detail', args=(news.id,))
    response = not_author_client.post(url, data=bad_words_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assertFormError(
        response.context['form'],
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, news, comment):
    url = reverse('news:delete', args=(news.id,))
    delete_url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url)
    assertRedirects(response, f'{delete_url}#comments')
    assert response.status_code, HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client,
        news,
        comment
):
    url = reverse('news:delete', args=(news.id,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, news, comment,
                                 form_comment_data
                                 ):
    url = reverse('news:edit', args=(news.id,))
    response = author_client.post(url, data=form_comment_data)
    edit_url = reverse('news:detail', args=(news.id,))
    assertRedirects(response, f'{edit_url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_comment_data['text']


def test_user_cant_edit_comment_of_another_user(not_author_client, news,
                                                comment, form_comment_data
                                                ):
    url = reverse('news:edit', args=(news.id,))
    response = not_author_client.post(url, data=form_comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    comment_from_bd = Comment.objects.get()
    assert comment.text == comment_from_bd.text
