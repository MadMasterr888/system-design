workspace {

    model {
        user = person "Пользователь" {
            description "Пользователь системы электронной почты."
        }

        emailSystem = softwareSystem "Приложение электронной почты" {
            description "Система для управления электронной почтой."

            userAccount = container "Учетная запись пользователя" {
                description "Хранит информацию о пользователе."
                technology "Java, Spring Boot"
            }

            mailFolder = container "Почтовая папка" {
                description "Содержит сообщения электронной почты."
                technology "Java, Spring Boot"
            }

            emailMessage = container "Сообщение" {
                description "Содержит данные о сообщении."
                technology "Java, Spring Boot"
            }

            db = container "База данных" {
                description "Хранит данные о пользователях и сообщениях."
                technology "PostgreSQL"
            }
        }

        user -> userAccount "Создает/находит пользователя"
        user -> mailFolder "Создает/получает почтовую папку"
        user -> emailMessage "Создает/получает сообщения"
    }

    views {
        theme default
        systemContext emailSystem {
            title "Диаграмма контекста приложения электронной почты"
            include *
            autolayout lr
        }

        container emailSystem {
            title "Контейнерная диаграмма приложения электронной почты"
            include *
            autolayout lr
        }

        dynamic emailSystem {
            title "Динамическая диаграмма отправки письма"

            user -> userAccount "Регистрация нового пользователя"
            user -> mailFolder "Создание новой почтовой папки"
            user -> emailMessage "Отправка нового письма"

            autolayout lr
        }
    }
}
