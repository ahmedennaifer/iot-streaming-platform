package consumer.processors

import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import java.sql.Timestamp
import java.time.Instant

class MetricsProcessorTest extends AnyFlatSpec with Matchers {

  println("Starting MetricsProcessor tests!")

  val spark = SparkSession
    .builder()
    .appName("MetricsProcessorTest")
    .master("local[2]")
    .getOrCreate()

  import spark.implicits._

  val testData = Seq(
    (
      "device1",
      "Temperature",
      "ON",
      25.0f,
      100.0f,
      Timestamp.from(Instant.now())
    ),
    (
      "device1",
      "Temperature",
      "ON",
      26.0f,
      95.0f,
      Timestamp.from(Instant.now())
    ),
    (
      "device2",
      "Humidity",
      "ERROR",
      30.0f,
      15.0f,
      Timestamp.from(Instant.now())
    )
  ).toDF(
    "DeviceId",
    "DeviceType",
    "Status",
    "CurrentReading",
    "BatteryLevel",
    "Timestamp"
  )

  "MetricsProcessor" should "calculate correct average readings by device type" in {
    val metrics = MetricsProcessor
      .calculateWindowedMetrics(testData)
      .select("DeviceType", "avg_reading")
      .collect()
      .map(row => (row.getString(0), row.getDouble(1)))
      .toMap

    metrics("Temperature") shouldBe 25.5 +- 0.1
    metrics("Humidity") shouldBe 30.0 +- 0.1
  }

  it should "identify devices with low battery" in {
    val health = MetricsProcessor
      .calculateDeviceHealth(testData)
      .select("DeviceType", "low_battery_count")
      .collect()
      .map(row => (row.getString(0), row.getLong(1)))
      .toMap

    health("Temperature") shouldBe 0
    health("Humidity") shouldBe 1
  }

  it should "count error states correctly" in {
    val health = MetricsProcessor
      .calculateDeviceHealth(testData)
      .select("DeviceType", "error_count")
      .collect()
      .map(row => (row.getString(0), row.getLong(1)))
      .toMap

    health("Temperature") shouldBe 0
    health("Humidity") shouldBe 1
  }

  it should "detect high temperature alerts" in {
    val alerts = MetricsProcessor
      .calculateAlertMetrics(testData)
      .select("DeviceType", "high_temp_alerts")
      .collect()
      .map(row => (row.getString(0), row.getLong(1)))
      .toMap

    alerts("Temperature") shouldBe 0
    alerts("Humidity") shouldBe 0
  }

  override def afterAll(): Unit = {
    spark.stop()
  }
}
