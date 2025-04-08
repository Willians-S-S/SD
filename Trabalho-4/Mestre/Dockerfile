FROM openjdk:17
WORKDIR /app
COPY . .
RUN javac MestreServer.java WorkerThread.java
CMD ["java", "MestreServer"]
