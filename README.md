## API Restaurant menu

API, which is being developed as part of a test task.

### Project Deployment

1.Clone repository

```
git clone https://github.com/6616454/test-task-the-restaurant-menu.git
```

2.Copy .env file

```
cp .envexample .env
```

3.Run the "make up" command for start project

```
make up
```

4.For tests run the "make up-tests" command
```
make up-tests
```
5.For run lint-instruments(pre-commit hook scripts) install dev dependencies and use the "make lint" command
```
poetry install --with dev

make lint
```

6.The application is available at

```
127.0.0.1:8000/docs
```
