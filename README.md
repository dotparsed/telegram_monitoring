# telegram_monitoring

Скрипт мониторинга чатов телеграм на появление ключевых слов. 
Входит через обычный профиль привязанный к телефону.
Проверяет чаты по порядку оценивает на то, как часто в них публикуют посты.
Чем реже в чат публикуют, тем реже скрипт проверяет чат. Если в чате давно не было постов, то заносит чат в черный список.

chats_test.txt - список чатов
result.txt - Найденые посты с данными чатов.
blacklist.txt - чаты в которые давно ничего не писали
