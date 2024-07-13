import sqlalchemy as sa

metadata = sa.MetaData()

KLineDataTable = sa.Table(
    'kline_data',
    metadata,
    sa.Column("timestamp", sa.BigInteger, primary_key=True, index=True),
    sa.Column("open", sa.Float, nullable=False),
    sa.Column("high", sa.Float, nullable=False),
    sa.Column("low", sa.Float, nullable=False),
    sa.Column("close", sa.Float, nullable=False),
    sa.Column("volume", sa.Float, nullable=False),
)
