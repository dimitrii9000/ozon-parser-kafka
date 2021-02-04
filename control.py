import time
import subprocess
import sys
import json


# Обёртка для subprocess'a
def exec_command(command):
    print(f"Executing '{command}'")
    try:
        output = subprocess.Popen(command.split(" "), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, encoding='utf8')

    except Exception as e:
        print(f"Exception while executing {command}: {e}")

    try:
        if output:
            print(output.stdout.read())
        if output.stderr:
            print(output.stderr.read())
    except: pass


arg = sys.argv[1]

if arg == "start":
    with open("settings.json", "r") as f:
        parser_instances = json.loads(f.read())["parser_instances"]

    exec_command("docker build -t ozon-worker worker/")
    exec_command("docker build -t ozon-parser parser/")

    # Т.К. IP можно выдавать только сетям, созданным вручную, то приходится создавать ее тут, а не в compose файле
    exec_command("docker network create --driver=bridge --subnet=173.18.0.0/16 kafka-ozon-network")

    exec_command(f"docker-compose up -d --scale ozon-parser={parser_instances}")
    time.sleep(5)

    # Создаем топики
    # Можно было их создать и с помощью KAFKA_CREATE_TOPICS, но тогда пришлось бы
    # регуляркой менять кол-во партиций в композ файле при изменении настроек
    exec_command(f"docker exec -i kafka /opt/kafka/bin/kafka-topics.sh --create --zookeeper zookeeper:2181 --replication-factor 1 --partitions {parser_instances} --topic ozon-category")
    exec_command("docker exec -i kafka /opt/kafka/bin/kafka-topics.sh --create --zookeeper zookeeper:2181 --replication-factor 1 --partitions 1 --topic ozon-products")

elif arg == "stop":
    exec_command("docker-compose down")

elif arg == "remove":
    exec_command("docker-compose down")
    # Удаляем сеть и имэджи
    exec_command("docker network rm kafka-ozon-network")
    exec_command("docker rmi ozon-worker")
    exec_command("docker rmi ozon-parser")

else:
    print("Incorrect argument")
