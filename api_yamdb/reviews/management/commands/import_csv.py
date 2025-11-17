import csv
import os

from django.core.management.base import BaseCommand
from django.db import transaction

from reviews.models import (
    Category, Comment, Genre, Review, Title, User
)


class Command(BaseCommand):
    help = 'Импорт данных из CSV файлов в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv_dir',
            type=str,
            default='static/data',
            help='Директория с CSV файлами'
        )

    def handle(self, *args, **options):
        csv_dir = options['csv_dir']

        # Проверяем существование директории
        if not os.path.exists(csv_dir):
            self.stdout.write(
                self.style.ERROR(f'Директория {csv_dir} не существует')
            )
            return

        # Импортируем данные в правильном порядке
        with transaction.atomic():
            self.import_users(csv_dir)
            self.import_categories(csv_dir)
            self.import_genres(csv_dir)
            self.import_titles(csv_dir)
            self.import_genre_title(csv_dir)
            self.import_reviews(csv_dir)
            self.import_comments(csv_dir)

        self.stdout.write(
            self.style.SUCCESS('Все данные успешно импортированы!')
        )

    def import_users(self, csv_dir):
        """Импорт пользователей"""
        file_path = os.path.join(csv_dir, 'users.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING('Файл users.csv не найден'))
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            users = []
            for row in reader:
                users.append(User(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=row['role'],
                    bio=row['bio'] or '',
                    first_name=row['first_name'] or '',
                    last_name=row['last_name'] or '',
                ))

            User.objects.bulk_create(users, ignore_conflicts=True)
            self.stdout.write(
                self.style.SUCCESS(f'Импортировано {len(users)} пользователей')
            )

    def import_categories(self, csv_dir):
        """Импорт категорий"""
        file_path = os.path.join(csv_dir, 'category.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(
                'Файл category.csv не найден'))
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            categories = []
            for row in reader:
                categories.append(Category(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug'],
                ))

            Category.objects.bulk_create(categories, ignore_conflicts=True)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Импортировано {len(categories)} категорий'
                )
            )

    def import_genres(self, csv_dir):
        """Импорт жанров"""
        file_path = os.path.join(csv_dir, 'genre.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING('Файл genre.csv не найден'))
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            genres = []
            for row in reader:
                genres.append(Genre(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug'],
                ))

            Genre.objects.bulk_create(genres, ignore_conflicts=True)
            self.stdout.write(
                self.style.SUCCESS(f'Импортировано {len(genres)} жанров')
            )

    def import_titles(self, csv_dir):
        """Импорт произведений"""
        file_path = os.path.join(csv_dir, 'titles.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING('Файл titles.csv не найден'))
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            titles = []
            for row in reader:
                try:
                    category = Category.objects.get(id=row['category'])
                    titles.append(Title(
                        id=row['id'],
                        name=row['name'],
                        year=row['year'],
                        category=category,
                        description='',
                    ))
                except Category.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Категория {row["category"]} не найдена'
                            f'для произведения {row["id"]}'
                        )
                    )

            Title.objects.bulk_create(titles, ignore_conflicts=True)
            self.stdout.write(
                self.style.SUCCESS(f'Импортировано {len(titles)} произведений')
            )

    def import_genre_title(self, csv_dir):
        """Импорт связей жанров и произведений"""
        file_path = os.path.join(csv_dir, 'genre_title.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(
                'Файл genre_title.csv не найден'))
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            relations_created = 0
            for row in reader:
                try:
                    title = Title.objects.get(id=row['title_id'])
                    genre = Genre.objects.get(id=row['genre_id'])
                    title.genre.add(genre)
                    relations_created += 1
                except (Title.DoesNotExist, Genre.DoesNotExist) as e:
                    self.stdout.write(
                        self.style.WARNING(f'Ошибка связи: {e}')
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Создано {relations_created} '
                    f'связей жанров с произведениями'
                )
            )

    def import_reviews(self, csv_dir):
        """Импорт отзывов"""
        file_path = os.path.join(csv_dir, 'review.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING('Файл review.csv не найден'))
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            reviews = []
            for row in reader:
                try:
                    title = Title.objects.get(id=row['title_id'])
                    author = User.objects.get(id=row['author'])
                    reviews.append(Review(
                        id=row['id'],
                        title=title,
                        text=row['text'],
                        author=author,
                        score=row['score'],
                        pub_date=row['pub_date'],
                    ))
                except (Title.DoesNotExist, User.DoesNotExist) as e:
                    self.stdout.write(
                        self.style.WARNING(f'Ошибка отзыва {row["id"]}: {e}')
                    )

            Review.objects.bulk_create(reviews, ignore_conflicts=True)
            self.stdout.write(
                self.style.SUCCESS(f'Импортировано {len(reviews)} отзывов')
            )

    def import_comments(self, csv_dir):
        """Импорт комментариев"""
        file_path = os.path.join(csv_dir, 'comments.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(
                'Файл comments.csv не найден'))
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            comments = []
            for row in reader:
                try:
                    review = Review.objects.get(id=row['review_id'])
                    author = User.objects.get(id=row['author'])
                    comments.append(Comment(
                        id=row['id'],
                        review=review,
                        text=row['text'],
                        author=author,
                        pub_date=row['pub_date'],
                    ))
                except (Review.DoesNotExist, User.DoesNotExist) as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Ошибка комментария {row["id"]}: {e}'
                        )
                    )

            Comment.objects.bulk_create(comments, ignore_conflicts=True)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Импортировано {len(comments)} комментариев'
                )
            )
