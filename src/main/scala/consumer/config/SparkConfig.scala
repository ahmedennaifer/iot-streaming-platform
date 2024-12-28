package consumer.config

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.types._

object SparkConfig {
  val schema = StructType(
    Array(
      StructField("DeviceId", StringType, nullable = false),
      StructField("DeviceModel", StringType, nullable = true),
      StructField("DeviceType", StringType, nullable = false),
      StructField("Status", StringType, nullable = false),
      StructField("CurrentReading", FloatType, nullable = false),
      StructField("BatteryLevel", FloatType, nullable = false),
      StructField("Location", FloatType, nullable = false),
      StructField("Timestamp", TimestampType, nullable = false)
    )
  )

  def createSparkSession(): SparkSession = {
    SparkSession.builder
      .appName("ScalaConsumer")
      .master("local[2]")
      .getOrCreate()
  }

  object WindowConfig {
    val windowDuration = "5 minutes"
    val slideDuration = "1 minute"
    val watermark = "10 minutes"
  }

  object KafkaConfig {
    val bootstrapServers = "kafka:9092"
    val topics = "temperature,humidity"
  }

  object DatabaseConfig {
    import consumer.config.Config
    
    val url = Config.DatabaseConfig.url
    val user = Config.DatabaseConfig.user
    val password = Config.DatabaseConfig.password
    val driver = Config.DatabaseConfig.driver
  }
}

// idealement dans un .env 
