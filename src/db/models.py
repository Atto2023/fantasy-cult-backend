#FastAPI Imports
from enum import Enum
import sqlalchemy as db
from datetime import datetime
import uuid 
from sqlalchemy import UniqueConstraint, func, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import JSONB,UUID
from sqlalchemy.ext.mutable import MutableDict

#Local Imports
from src.db.database import Base

class MasterCity(Base):
    __tablename__="master_city"
    city_id = db.Column(UUID(as_uuid=True), primary_key=True,index=True,default=uuid.uuid4)
    state = db.Column(UUID(as_uuid=True),db.ForeignKey("master_state.state_id"))
    city = db.Column(db.String,nullable=True)

    __table_args__ = (
        UniqueConstraint('state', 'city', name='unique_city'),
    )

class MasterState(Base):
    __tablename__="master_state"
    state_id  = db.Column(UUID(as_uuid=True), primary_key=True,index=True,default=uuid.uuid4)
    country = db.Column(UUID(as_uuid=True),db.ForeignKey ("master_country.country_id"))
    state = db.Column(db.String,nullable=True)

    __table_args__ = (
        UniqueConstraint('country', 'state', name='unique_state'),
    )

class MasterCountry(Base):
    __tablename__ = "master_country"
    country_id = db.Column(UUID(as_uuid=True), primary_key=True,index=True,default=uuid.uuid4)
    name = db.Column(db.String, nullable=True, unique = True)

class User(Base):
    __tablename__= 'user'
    user_id = db.Column(UUID(as_uuid=True), primary_key=True,index=True,default=uuid.uuid4)
    name = db.Column(db.String,nullable=True)
    dob = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String,nullable=True) # TODO : Check on the controller level for "Male", "Female", "Others"
    profile_image = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True, unique=True)
    mobile = db.Column(db.String, unique=True)
    address = db.Column(db.String, nullable=True)
    city = db.Column(UUID(as_uuid=True),db.ForeignKey('master_city.city_id'),nullable=True)
    state = db.Column(UUID(as_uuid=True),db.ForeignKey('master_state.state_id'),nullable=True)
    country = db.Column(UUID(as_uuid=True),db.ForeignKey('master_country.country_id'),nullable=True)
    pin_code = db.Column(db.String, nullable=True)
    team_name = db.Column(db.String, nullable=True)
    referral_code = db.Column(db.String, nullable=True)
    is_email_verified = db.Column(db.Boolean,default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    is_active = db.Column(db.Boolean,default=True)

class EmailOTP(Base):
    __tablename__='email_otp'
    email_otp_id = db.Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    email = db.Column(db.String, nullable=False)
    otp = db.Column(db.String,nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class MobileOTP(Base):
    __tablename__='mobile_otp'
    mobile_otp_id = db.Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    mobile = db.Column(db.String, nullable=False)
    otp = db.Column(db.String,nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class VerificationEnum(Enum):
    UNVERIFIED = 'Unverified'
    REJECTED = 'Rejected'
    VERIFIED = 'Verified'

class PanVerification(Base):
    __tablename__='pan_verification'
    pan_verfication_id  = db.Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True),db.ForeignKey('user.user_id'))
    pan_name = db.Column(db.String(255),nullable=False)
    pan_number = db.Column(db.String,nullable=False)
    date_of_birth = db.Column(db.Date,nullable=False)
    pan_s3_url = db.Column(db.String,nullable=False)
    status = db.Column(db.Enum(VerificationEnum), default = VerificationEnum.UNVERIFIED)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class BankVerificationEnum(Enum):
    UNVERIFIED = 'Unverified'
    REJECTED = 'Rejected'
    VERIFIED = 'Verified'

class BankVerification(Base):
    __tablename__ = 'bank_verification'
    bank_verification_id = db.Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True),db.ForeignKey('user.user_id'))
    name = db.Column(db.String(255),nullable=False)
    account_number = db.Column(db.String(255),nullable=False)
    ifsc_code = db.Column(db.String(255),nullable=False)
    bank_name = db.Column(db.String(255),nullable=False)
    branch_name = db.Column(db.String,nullable=False)
    state = db.Column(db.String,nullable=False)
    bank_s3_url = db.Column(db.String,nullable=False)
    status = db.Column(db.Enum(BankVerificationEnum), default = BankVerificationEnum.UNVERIFIED)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class UserBalance(Base):
    __tablename__ = 'user_balance'
    balance_id = db.Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True),db.ForeignKey('user.user_id'))
    added_amount = db.Column(db.Float,nullable=True)
    winning_amount = db.Column(db.Float,nullable=True)
    cash_bonus_amount = db.Column(db.Float,nullable=True)
    amount = db.Column(db.Float,nullable=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class TransactionTypeEnum(Enum):
    DEPOSIT_MONEY = 'Deposit Money'
    JOIN_CONTEST = 'Join Contest'
    WON_MONEY = 'Won Money'
    CASH_BONUS = 'Cash Bonus'
    WITHDRAW_MONEY = 'Withdraw Money'
    CANCELLED_CONTEST = 'Cancelled Contest'

class TransactionStatusEnum(Enum):
    COMPLETED = 'Completed'
    FAILED = 'Failed'
    PENDING = 'Pending'

class UserTransaction(Base):
    __tablename__ = 'user_transaction'
    transaction_id = db.Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True),db.ForeignKey('user.user_id'))
    amount = db.Column(db.Float,nullable=True)
    transaction_type = db.Column(db.Enum(TransactionTypeEnum))
    transaction_status = db.Column(db.Enum(TransactionStatusEnum))
    meta_data = db.Column(MutableDict.as_mutable(JSONB), nullable=True)
    deduct_add = db.Column(db.Float,nullable=True)
    deduct_win = db.Column(db.Float,nullable=True)
    deduct_cash = db.Column(db.Float,nullable=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())


class CricketSeries(Base):
    __tablename__ = "cricket_series"
    cricket_series_id  = db.Column(UUID(as_uuid=True), primary_key=True,index=True,default=uuid.uuid4)
    series_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String, nullable=True)
    fc_name = db.Column(db.String, nullable=True)
    use_name = db.Column(db.Boolean, default=False)
    short_name = db.Column(db.String,nullable=True)
    series_category = db.Column(db.String, nullable=True)
    series_type = db.Column(db.String, nullable=True)
    series_start_date = db.Column(db.DateTime, default=None)
    series_end_date = db.Column(db.DateTime, default=None)
    team_id = db.Column(db.ARRAY(UUID))
    is_live = db.Column(db.Boolean, default = False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class CricketMatch(Base):
    __tablename__='cricket_match'
    cricket_match_id = db.Column(UUID(as_uuid=True), primary_key=True,index=True,default=uuid.uuid4)
    match_id = db.Column(db.Integer, unique=True) # match_id
    series_id = db.Column(db.ForeignKey('cricket_series.cricket_series_id'), nullable=False)
    match_format = db.Column(db.String,nullable=True)
    team_a = db.Column(db.ForeignKey('cricket_team.cricket_team_id'),nullable=False)
    team_b = db.Column(db.ForeignKey('cricket_team.cricket_team_id'),nullable=False)
    match_start_time = db.Column(db.DateTime,default = None)
    match_end_time = db.Column(db.DateTime,default = None)
    last_update_on = db.Column(db.DateTime, default=None)
    is_live = db.Column(db.Boolean, default = False)
    is_point_added = db.Column(db.Boolean, default = False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    def __str__(self):
        return f"{self.match_id}"

class CricketPlayer (Base):
    __tablename__ = 'cricket_player'
    cricket_player_id = db.Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    player_id = db.Column(db.Integer, unique=True)
    title = db.Column(db.String,nullable=True)
    short_name = db.Column(db.String,nullable=True)
    first_name = db.Column(db.String,nullable=True)
    last_name = db.Column(db.String,nullable=True)
    middle_name = db.Column(db.String,nullable=True)
    thumb_url = db.Column(db.String,nullable=True)
    team = db.Column(db.String,nullable=True)
    playing_role = db.Column(db.String,nullable=True)
    batting_style = db.Column(db.String,nullable=True)
    bowling_style = db.Column(db.String,nullable=True)
    batting_stats = db.Column(MutableDict.as_mutable(JSONB), nullable=True)
    bowling_stats = db.Column(MutableDict.as_mutable(JSONB), nullable=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class CricketTeam(Base):
    __tablename__ = 'cricket_team'
    cricket_team_id = db.Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    team_id = db.Column(db.Integer, unique = True) 
    name = db.Column(db.String,nullable=False)
    fc_short_name = db.Column(db.String,nullable=True)
    use_short_name = db.Column(db.Boolean, default=False)
    short_name = db.Column(db.String,nullable=True)
    team_type = db.Column(db.String, nullable = True)
    thumb_url = db.Column(db.String,nullable = True)
    logo_url = db.Column(db.String,nullable = True)
    fc_logo_url = db.Column(db.String,nullable = True)
    use_logo_url = db.Column(db.Boolean, default=False)
    country = db.Column(db.String, nullable = True)
    sex = db.Column(db.String, nullable = True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())


class CricketSeriesSquad(Base):
    __tablename__ = 'cricket_series_squad'
    cricket_series_squad_id = db.Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    series_id = db.Column(db.ForeignKey('cricket_series.cricket_series_id'), nullable=False)
    team_id = db.Column(db.ForeignKey('cricket_team.cricket_team_id'),nullable=False)
    player_id = db.Column(db.ARRAY(UUID))

class CricketSeriesMatchPoints(Base):
    __tablename__ = 'cricket_series_match_point'
    cricket_series_match_point_id = db.Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    cricket_series_id = db.Column(db.ForeignKey('cricket_series.cricket_series_id'), nullable=False)
    series_id = db.Column(db.Integer)
    cricket_match_id = db.Column(db.ForeignKey('cricket_match.cricket_match_id'), nullable=False)
    match_id = db.Column(db.Integer)
    cricket_player_id = db.Column(UUID(as_uuid=True),db.ForeignKey('cricket_player.cricket_player_id'), nullable = True)
    player_id = db.Column(db.Integer)
    points = db.Column(db.Float, default=0.0)

class DraftForEnum(Enum):
    SERIES = 'Series'
    MATCH = 'Match'

class UserDraft(Base):
    __tablename__ = 'user_draft'
    user_draft_id = db.Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True),db.ForeignKey('user.user_id'))
    league_name = db.Column(db.String, nullable=True)
    invitation_code = db.Column(db.String)
    max_playing_user = db.Column(db.Integer, nullable=True)
    entry_amount = db.Column(db.Float,nullable=True)
    total_amount = db.Column(db.Float,nullable=True)
    fantasy_commission = db.Column(db.Float,nullable=True)
    winners_price = db.Column(MutableDict.as_mutable(JSONB), nullable=True)
    player_choice = db.Column(MutableDict.as_mutable(JSONB), nullable=True)
    draft_for = db.Column(db.Enum(DraftForEnum))
    draft_match_series_id = db.Column(UUID(as_uuid=True))
    is_draft_completed = db.Column(db.Boolean, default=False)
    is_result_announce = db.Column(db.Boolean, default=False)
    is_draft_cancelled = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=False)
    is_captain_allowed = db.Column(db.Boolean, default=True)
    is_cancelled_pushed = db.Column(db.Boolean, default=False)
    is_draft_pushed = db.Column(db.Boolean, default=False)
    number_of_round = db.Column(db.Integer, nullable=True)
    top_picks = db.Column(db.Integer, nullable=True)
    draft_starting_time = db.Column(db.DateTime, nullable=True)
    player_selected = db.Column(db.ARRAY(UUID))
    match_id_point = db.Column(db.ARRAY(UUID), nullable=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())


class ContestStatusEnum(Enum):
    UPCOMING = 'Upcoming'
    LIVE = 'Live'
    COMPLETED = 'Completed'

class ContestPlayers(Base):
    __tablename__ = 'contest_player'
    contest_player_id = db.Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    draft_id = db.Column(UUID(as_uuid=True),db.ForeignKey('user_draft.user_draft_id'))
    user_id = db.Column(UUID(as_uuid=True),db.ForeignKey('user.user_id'))
    player_selected = db.Column(db.ARRAY(UUID))
    captain = db.Column(UUID(as_uuid=True),db.ForeignKey('cricket_player.cricket_player_id'), nullable = True)
    vice_captain = db.Column(UUID(as_uuid=True),db.ForeignKey('cricket_player.cricket_player_id'), nullable = True)
    position = db.Column(db.Integer, nullable=True)
    points = db.Column(db.Float,nullable=True)
    amount = db.Column(db.Float,nullable=True)
    status = db.Column(db.Enum(ContestStatusEnum), default = ContestStatusEnum.UPCOMING)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class GST(Base):
    __tablename__ = 'gst'
    gst_id = db.Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    percentage = db.Column(db.Float,nullable=True)
    name = db.Column(db.String,nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class GstCalculation(Base):
    __tablename__ = 'gst_calculation'
    gst_calculation_id = db.Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    amount = db.Column(db.Float,nullable=False)
    gst_value = db.Column(db.Float,nullable=False)
    total = db.Column(db.Float,nullable=False)
    user_id = db.Column(UUID(as_uuid=True),db.ForeignKey('user.user_id'))
    month = db.Column(db.Integer,nullable=False)
    year = db.Column(db.Integer,nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class TDS(Base):
    __tablename__ = 'tds'
    tds_id = db.Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    percentage = db.Column(db.Float,nullable=True)
    name = db.Column(db.String,nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class TdsCalculation(Base):
    __tablename__ = 'tds_calculation'
    tds_calculation_id = db.Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    amount = db.Column(db.Float,nullable=False)
    tds_value = db.Column(db.Float,nullable=False)
    total = db.Column(db.Float,nullable=False)
    user_id = db.Column(UUID(as_uuid=True),db.ForeignKey('user.user_id'))
    month = db.Column(db.Integer,nullable=False)
    year = db.Column(db.Integer,nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class CashBonusDiscount(Base):
    __tablename__ = 'cash_bonus_discount'
    cash_bonus_discount_id = db.Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    percentage = db.Column(db.Float,nullable=True)
    name = db.Column(db.String,nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Notification(Base):
    __tablename__='notification'
    notification_id = db.Column((UUID(as_uuid=True)), primary_key=True,index=True,default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True),db.ForeignKey('user.user_id'))
    message = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    is_pushed = db.Column(db.Boolean, default=False)
    meta_data = db.Column(MutableDict.as_mutable(JSONB), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class UserDevice(Base):
    __tablename__ = "user_device"
    device_id = db.Column((UUID(as_uuid=True)), primary_key=True,index=True,default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True),db.ForeignKey('user.user_id'))
    device_token = db.Column(db.String,nullable=False)

class HomeScreen(Base):
    __tablename__ = "home_screen"
    homescreen_id = db.Column((UUID(as_uuid=True)), primary_key=True,index=True,default=uuid.uuid4)
    image = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
