package consumer

import slick.jdbc.PostgresProfile.api._
import scala.concurrent.{Await, Future}
import scala.concurrent.duration._
import scala.util.{Failure, Success, Try}
import scala.concurrent.ExecutionContext.Implicits.global

case class Data(
    id: Option[Int] = None,
    deviceModel: String,
    deviceType: String,
    status: String,
    currentReading: Float,
    batteryLevel: Float,
    age: Int
)

class DataTable(tag: Tag) extends Table[Data](tag, "data") {
  def id = column[Int]("id", O.PrimaryKey, O.AutoInc)
  def deviceModel = column[String]("device_model")
  def deviceType = column[String]("device_type")
  def status = column[String]("status")
  def currentReading = column[Float]("current_reading")
  def batteryLevel = column[Float]("battery_level")
  def age = column[Int]("age")

  def * = (
    id.?,
    deviceModel,
    deviceType,
    status,
    currentReading,
    batteryLevel,
    age
  ) <> (Data.tupled, Data.unapply)
}
object database {
  val dataTable = TableQuery[DataTable]

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

    val setup = DBIO.seq(dataTable.schema.createIfNotExists)
    Await.result(db.run(setup), 5.seconds)
    println("Table created successfully!")

    val checkQuery: Future[Int] = db.run(sql"SELECT 1".as[Int].head)
    Try(Await.result(checkQuery, 2.seconds)) match {
      case Success(_) => println("DB is up")
      case Failure(_) => println("DB is not up")
    }
  }
}
