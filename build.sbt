ThisBuild / scalaVersion := "2.12.16"

lazy val root = (project in file("."))
  .settings(
    name := "Spark test",
    version := "0.1",
    libraryDependencies ++= Seq(
      "org.apache.spark" %% "spark-core" % "3.5.3",
      "org.apache.spark" %% "spark-sql" % "3.5.3",
      "org.apache.spark" %% "spark-streaming" % "3.5.3",
      "org.apache.spark" %% "spark-sql-kafka-0-10" % "3.5.3",
      "org.tpolecat" %% "skunk-core" % "0.6.4"
    ),
    Compile / mainClass := Some("consumer.SparkConsumer")
  )
