import pytest
from pytest_lazy_fixtures import lf

from django.conf import settings
from django.urls import reverse


# @pytest.mark.django_db
# def test_news_count(client, news_list):
#         # Загружаем главную страницу.
#         response = client.get(HOME_URL)
#         # Код ответа не проверяем, его уже проверили в тестах маршрутов.
#         # Получаем список объектов из словаря контекста.
#         object_list = response.context['object_list']
#         # Определяем количество записей в списке.
#         news_count = object_list.count()
#         # Проверяем, что на странице именно 10 новостей.
#         assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


# @pytest.mark.django_db
# def test_news_order(client, news_list):
#         response = client.get(HOME_URL)
#         object_list = response.context['object_list']
#         # Получаем даты новостей в том порядке, как они выведены на странице.
#         all_dates = [news.date for news in object_list]
#         # Сортируем полученный список по убыванию.
#         sorted_dates = sorted(all_dates, reverse=True)
#         # Проверяем, что исходный список был отсортирован правильно.
#         assert all_dates == sorted_dates


@pytest.mark.django_db
def test_news_count_and_order(client, news_list):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_comments_order(client, news_with_comment_list):
    url = reverse('news:detail', args=(news_with_comment_list.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
@pytest.mark.parametrize(
    # Задаём названия для параметров:
    'parametrized_client, form_in_context',
    (
        # Передаём фикстуры в параметры при помощи "ленивых фикстур":
        (lf('author_client'), True),
        (lf('client'), False),
    )
)
def test_existing_form_for_different_clients(news, parametrized_client,
                                             form_in_context
                                             ):
    url = reverse('news:detail', args=(news.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) == form_in_context
