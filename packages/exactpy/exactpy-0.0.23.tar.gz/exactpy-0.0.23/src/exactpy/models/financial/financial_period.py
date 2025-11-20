from sparkdantic import SparkField

from exactpy.models.base import ExactOnlineBaseModel
from exactpy.types import GUID, ExactUnixTimestamp


class FinancialPeriodModel(ExactOnlineBaseModel):
    _pk = "id"
    id: GUID = SparkField(spark_type="string")
    created: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    creator: GUID = SparkField(spark_type="string")
    creator_full_name: str | None = SparkField(spark_type="string", default=None)
    division: int | None = SparkField(spark_type="integer", default=None)
    end_date: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    fin_period: int | None = SparkField(spark_type="integer", default=None)
    fin_year: int | None = SparkField(spark_type="integer", default=None)
    modified: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    modifier: GUID = SparkField(spark_type="string")
    modifier_full_name: str | None = SparkField(spark_type="string", default=None)
    start_date: ExactUnixTimestamp = SparkField(spark_type="timestamp")
