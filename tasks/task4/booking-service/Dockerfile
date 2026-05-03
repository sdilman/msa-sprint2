# Используем официальный минимальный образ Go
FROM golang:1.21-alpine

# Добавляем необходимые пакеты
RUN apk add --no-cache curl

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем Go-файл
COPY main.go .

# Создаем минимальный go.mod
RUN echo "module booking-service" > go.mod && \
    echo "" >> go.mod && \
    echo "go 1.21" >> go.mod

# Собираем бинарник из main.go
RUN go build -o booking-service main.go

# Задаем команду запуска
CMD ["./booking-service"]