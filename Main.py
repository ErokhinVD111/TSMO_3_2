import random
import math

# Создаем класс-канал
class Channel:
    def __init__(self):
        # Поле активен канал или нет
        self.is_active = False
        # Поле индекса заявки
        self.index_request = 0
        # Поле время занятости канала
        self.time_busy = 0.0
        # Поле прихода заявки
        self.time_coming_request = 0.0

class ServiceSystem:
    def __init__(self, number_of_channels, number_of_channels_parallel):
        # Список каналов
        self.channels = []
        # Список занятых каналов на каждой итерации
        self.busy_channels = []
        # key - индекс заявки, value - кол-во каналов обр. заявку
        self.request_channels_pair = {}
        # Кол-во заявок пришедших в систему
        self.count_request = 0
        # Кол-во выполенных заявок
        self.count_request_complete = 0
        # Кол-во отклоненных заявок
        self.count_request_denied = 0
        # Кол-во каналов в системе
        self.number_of_channels = number_of_channels
        # Кол-во каналов для взаимопомощи
        self.number_of_channels_parallel = number_of_channels_parallel
        # Устанавливем начальные значения в системе
        self.set_default_system()
        # Начальные характеристики системы
        self.base_characteristics = BaseCharacteristics()
        # Калькулятор времени
        self.time_calculator = TimeCalculator()

    # Метод для установки начальных значений в системе
    def set_default_system(self):
        for iter in range(self.number_of_channels):
            self.channels.append(Channel())

    # Метод для поиска свободных каналов
    def find_free_channels(self):
        free_channels = 0
        for channel in self.channels:
            if channel.is_active == False:
                free_channels += 1

        if free_channels >= self.number_of_channels_parallel:
            free_channels = self.number_of_channels_parallel
        elif free_channels == 0:
            free_channels = 0

        return free_channels

    # Метод для поиска занятых каналов
    def find_busy_channels(self):
        busy_channels = 0
        for channel in self.channels:
            if channel.is_active == True:
                busy_channels += 1
        return busy_channels

    # Метод для обновления каналов
    def update_channels(self, time_coming_request):
        for channel in self.channels:
            if channel.is_active == True:
                if channel.time_coming_request + channel.time_busy <= time_coming_request:
                    channel.is_active = False
                    if channel.index_request in self.request_channels_pair.keys():
                        del self.request_channels_pair[channel.index_request]
        self.support()

    # Метод для взаимопомощи между каналами
    def support(self):
        for list_channels in self.request_channels_pair.values():
            # Если найдутся свободные каналы
            recalculate_time = False
            for ch in self.channels:
                # Проверяем, что каналам нужна помощь
                if len(list_channels) < self.number_of_channels_parallel:
                    # Находим свободные канал и добавляем их к занятым каналам
                    if ch.is_active == False:
                        ch.is_active = True
                        ch.index_request = list_channels[0].index_request
                        ch.time_coming_request = list_channels[0].time_coming_request
                        list_channels.append(ch)
                        recalculate_time = True

            # Если нашлись свободные каналы, то пересчитываем время
            if recalculate_time:
                time_busy_channels = self.time_calculator.calculate_time_busy(self.base_characteristics.l,
                                                                              self.base_characteristics.mu,
                                                                              len(list_channels))
                for channel in list_channels:
                    channel.time_busy = time_busy_channels


    def update_count_request(self, count_free_channels):
        if count_free_channels > 0:
            self.count_request_complete += 1
        else:
            self.count_request_denied += 1
        self.count_request += 1

    # Метод для обработки заявки каналами
    def add_request(self, time_coming_request, time_busy, index_request):

        # Обновление каналов, если вышло время обслуживания
        self.update_channels(time_coming_request)

        # Перераспределение
        self.redistribution_channels()

        free_channels = self.find_free_channels()
        #Обновление кол-ва заявок
        self.update_count_request(free_channels)

        # В цикле ставится заявка на обслуживание
        for channel in self.channels:
            if free_channels == 0:
                break
            if channel.is_active == False:
                channel.is_active = True
                channel.time_coming_request = time_coming_request
                channel.time_busy = time_busy
                channel.index_request = index_request
                if channel.index_request not in self.request_channels_pair.keys():
                    self.request_channels_pair[index_request] = []
                self.request_channels_pair[index_request].append(channel)
                free_channels -= 1


    # Перераспределение каналов
    def redistribution_channels(self):
        # Кол-во заявок в системе
        count_request_in_system = len(self.request_channels_pair.keys())
        if count_request_in_system + 1 <= self.number_of_channels:
            for list_channels in self.request_channels_pair.values():
                # Если есть кол-во каналов, обрабатывающих заявку > 1,
                # то убираем один канал из обслуживания для вновь прибывшей заявки
                if self.number_of_channels - self.find_busy_channels() == 0:
                    if len(list_channels) > 1:
                        temp_channel = list_channels.pop()
                        temp_channel.is_active = False
                        time_busy_channels = self.time_calculator.calculate_time_busy(self.base_characteristics.l,
                                                                                      self.base_characteristics.mu,
                                                                                      len(list_channels))
                        # Пересчитываем время для каналов, от которых оторвали один канал
                        for channel in list_channels:
                            channel.time_busy = time_busy_channels

class TimeCalculator:
    def __init__(self):
        self.time_modelling = 1000000
        self.time_coming = 0

    # Метод для расчета времени обслуживания
    def calculate_time_busy(self, l, mu, number_of_channels):
        if number_of_channels >= l:
            number_of_channels = l
        elif number_of_channels == 0:
            number_of_channels = 1
        return ((-1 / (mu)) * math.log(random.random())) / number_of_channels

    # Метод для расчета времени прихода заявки
    def calculate_time_coming(self, lamda):
        self.time_coming += (-1 / lamda) * math.log(random.random())
        return self.time_coming

# Класс с базовыми характеристиками

"""
mu_mid = 1/2 # скорострельность каждой установки
a = 35 # Длинна обстрела
p = 0.57 # Вероятность поражения цели одной ракетой
V = 1700/60 # Скорость ракеты в минутах
q =3 # Количество устанвоок
I = 5 # Средний линейный интервал между ракетами
l = 3 # Кол-во взаимопомагающих каналов
n = [3,4,5,6]
mu = mumid * p * q
lambda = V/I
"""
class BaseCharacteristics:
    def __init__(self):
        self.mu_single = 1/2
        self.a = 35
        self.p = 0.57
        self.V = 1700/60
        self.q = 3
        self.I = 5
        self.l = 3
        self.n = [3, 4, 5, 6]
        self.mu = self.mu_single * self.p * self.q
        self.lamda = self.V / self.I


if __name__ == '__main__':
    base_characteristics = BaseCharacteristics()
    time_calculator = TimeCalculator()
    service_system = ServiceSystem(base_characteristics.n[0], base_characteristics.l)

    # Запускаем основной цикл
    for k in range(time_calculator.time_modelling):
        service_system.busy_channels.append(service_system.find_busy_channels())
        time_coming = time_calculator.calculate_time_coming(base_characteristics.lamda)
        time_busy_channels = time_calculator.calculate_time_busy(
             base_characteristics.l, base_characteristics.mu, service_system.find_free_channels())
        service_system.add_request(time_coming, time_busy_channels, k)


    print(f"Число заявок:{service_system.count_request}")
    print(f"Число выполненых заявок:{service_system.count_request_complete}")
    print(f"Число отклоненных заявок:{service_system.count_request_denied}")
    print(f"Вероятность обслуживания:{service_system.count_request_complete/service_system.count_request}")
    print(f"Среднее число занятых каналов в системе:{sum(service_system.busy_channels)/time_calculator.time_modelling}")


