package consumer

import slick.jdbc.PostgresProfile.api._
import scala.concurrent.{Await, Future}
import scala.concurrent.duration._
import scala.util.{Failure, Success, Try}
import scala.concurrent.ExecutionContext.Implicits.global
import java.sql.Timestamp

case class Data(
    DeviceId: String,
    DeviceModel: String,
    DeviceType: String,
    Status: String,
    CurrentReading: Float,
    BatteryLevel: Float,
    Location: Float,
    Timestamp: Timestamp
)

case class WindowedMetrics(
    window_start: Timestamp,
    window_end: Timestamp,
    DeviceType: String,
    avg_reading: Double,
    max_reading: Double,
    min_reading: Double,
    stddev_reading: Double,
    avg_battery: Double,
    number_of_readings: Long
)

case class DeviceHealth(
    window_start: Timestamp,
    window_end: Timestamp,
    DeviceType: String,
    avg_battery: Double,
    error_count: Long,
    low_battery_count: Long
)

case class AlertMetrics(
    window_start: Timestamp,
    window_end: Timestamp,
    DeviceType: String,
    high_temp_alerts: Long,
    critical_battery_alerts: Long,
    error_alerts: Long
)

class DataTable(tag: Tag) extends Table[Data](tag, "data") {
  def DeviceId = column[String]("DeviceId")
  def DeviceModel = column[String]("DeviceModel")
  def DeviceType = column[String]("DeviceType")
  def Status = column[String]("Status")
  def CurrentReading = column[Float]("CurrentReading")
  def BatteryLevel = column[Float]("BatteryLevel")
  def Location = column[Float]("Location")
  def Timestamp = column[Timestamp]("Timestamp")

  def * = (
    DeviceId,
    DeviceModel,
    DeviceType,
    Status,
    CurrentReading,
    BatteryLevel,
    Location,
    Timestamp
  ) <> (Data.tupled, Data.unapply)
}

class WindowedMetricsTable(tag: Tag) extends Table[WindowedMetrics](tag, "windowed_metrics") {
  def window_start = column[Timestamp]("window_start")
  def window_end = column[Timestamp]("window_end")
  def DeviceType = column[String]("DeviceType")
  def avg_reading = column[Double]("avg_reading")
  def max_reading = column[Double]("max_reading")
  def min_reading = column[Double]("min_reading")
  def stddev_reading = column[Double]("stddev_reading")
  def avg_battery = column[Double]("avg_battery")
  def number_of_readings = column[Long]("number_of_readings")

  def * = (
    window_start,
    window_end,
    DeviceType,
    avg_reading,
    max_reading,
    min_reading,
    stddev_reading,
    avg_battery,
    number_of_readings
  ) <> (WindowedMetrics.tupled, WindowedMetrics.unapply)

  def idx = index("idx_windowed_metrics_time", (window_start, window_end))
}

class DeviceHealthTable(tag: Tag) extends Table[DeviceHealth](tag, "device_health") {
  def window_start = column[Timestamp]("window_start")
  def window_end = column[Timestamp]("window_end")
  def DeviceType = column[String]("DeviceType")
  def avg_battery = column[Double]("avg_battery")
  def error_count = column[Long]("error_count")
  def low_battery_count = column[Long]("low_battery_count")

  def * = (
    window_start,
    window_end,
    DeviceType,
    avg_battery,
    error_count,
    low_battery_count
  ) <> (DeviceHealth.tupled, DeviceHealth.unapply)

  def idx = index("idx_device_health_time", (window_start, window_end))
}

class AlertMetricsTable(tag: Tag) extends Table[AlertMetrics](tag, "alert_metrics") {
  def window_start = column[Timestamp]("window_start")
  def window_end = column[Timestamp]("window_end")
  def DeviceType = column[String]("DeviceType")
  def high_temp_alerts = column[Long]("high_temp_alerts")
  def critical_battery_alerts = column[Long]("critical_battery_alerts")
  def error_alerts = column[Long]("error_alerts")

  def * = (
    window_start,
    window_end,
    DeviceType,
    high_temp_alerts,
    critical_battery_alerts,
    error_alerts
  ) <> (AlertMetrics.tupled, AlertMetrics.unapply)

  def idx = index("idx_alert_metrics_time", (window_start, window_end))
}

object database {
  val dataTable = TableQuery[DataTable]
  val windowedMetricsTable = TableQuery[WindowedMetricsTable]
  val deviceHealthTable = TableQuery[DeviceHealthTable]
  val alertMetricsTable = TableQuery[AlertMetricsTable]

  def main(args: Array[String]): Unit = {
    getDatabase()
  }

  def getDatabase(): Unit = {
    val db = Database.forURL(
      url = "jdbc:postgresql://db:5432/iot",
      user = "nafra",
      password = "test",
      driver = "org.postgresql.Driver"
    )

    val dropTables = DBIO.seq(
      sqlu"DROP TABLE IF EXISTS windowed_metrics",
      sqlu"DROP TABLE IF EXISTS device_health",
      sqlu"DROP TABLE IF EXISTS alert_metrics"
    )

    val setup = DBIO.seq(
      windowedMetricsTable.schema.createIfNotExists,
      deviceHealthTable.schema.createIfNotExists,
      alertMetricsTable.schema.createIfNotExists
    )

    Await.result(db.run(dropTables), 5.seconds)
    Await.result(db.run(setup), 5.seconds)
    println("Tables recreated successfully!")

    val checkQuery: Future[Int] = db.run(sql"SELECT 1".as[Int].head)
    Try(Await.result(checkQuery, 2.seconds)) match {
      case Success(_) => println("DB is up")
      case Failure(_) => println("DB is not up")
    }
  }
}
