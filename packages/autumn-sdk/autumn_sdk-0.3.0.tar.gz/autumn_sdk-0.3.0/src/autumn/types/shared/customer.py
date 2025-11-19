# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = [
    "Customer",
    "Balances",
    "BalancesReset",
    "BalancesBreakdown",
    "BalancesBreakdownReset",
    "BalancesFeature",
    "BalancesFeatureCreditSchema",
    "BalancesFeatureDisplay",
    "BalancesRollover",
    "Subscription",
    "SubscriptionPlan",
    "SubscriptionPlanFeature",
    "SubscriptionPlanFeaturePrice",
    "SubscriptionPlanFeaturePriceTier",
    "SubscriptionPlanFeatureReset",
    "SubscriptionPlanFeatureDisplay",
    "SubscriptionPlanFeatureFeature",
    "SubscriptionPlanFeatureFeatureCreditSchema",
    "SubscriptionPlanFeatureFeatureDisplay",
    "SubscriptionPlanFeatureProration",
    "SubscriptionPlanFeatureRollover",
    "SubscriptionPlanPrice",
    "SubscriptionPlanPriceDisplay",
    "SubscriptionPlanCustomerEligibility",
    "SubscriptionPlanFreeTrial",
    "Entity",
    "Invoice",
    "Referral",
    "ReferralCustomer",
    "Rewards",
    "RewardsDiscount",
    "TrialsUsed",
    "UpcomingInvoice",
    "UpcomingInvoiceDiscount",
    "UpcomingInvoiceLine",
]


class BalancesReset(BaseModel):
    interval: Literal["one_off", "minute", "hour", "day", "week", "month", "quarter", "semi_annual", "year", "multiple"]

    resets_at: Optional[float] = None

    interval_count: Optional[float] = None


class BalancesBreakdownReset(BaseModel):
    interval: Literal["one_off", "minute", "hour", "day", "week", "month", "quarter", "semi_annual", "year", "multiple"]

    resets_at: Optional[float] = None

    interval_count: Optional[float] = None


class BalancesBreakdown(BaseModel):
    current_balance: float

    granted_balance: float

    max_purchase: Optional[float] = None

    overage_allowed: bool

    purchased_balance: float

    reset: Optional[BalancesBreakdownReset] = None

    usage: float


class BalancesFeatureCreditSchema(BaseModel):
    credit_cost: float

    metered_feature_id: str


class BalancesFeatureDisplay(BaseModel):
    plural: Optional[str] = None

    singular: Optional[str] = None


class BalancesFeature(BaseModel):
    id: str

    archived: bool

    consumable: bool

    name: str

    type: Literal["boolean", "metered", "credit_system"]

    credit_schema: Optional[List[BalancesFeatureCreditSchema]] = None

    display: Optional[BalancesFeatureDisplay] = None

    event_names: Optional[List[str]] = None


class BalancesRollover(BaseModel):
    balance: float

    expires_at: float


class Balances(BaseModel):
    current_balance: float

    feature_id: str

    granted_balance: float

    max_purchase: Optional[float] = None

    overage_allowed: bool

    purchased_balance: float

    reset: Optional[BalancesReset] = None

    unlimited: bool

    usage: float

    breakdown: Optional[List[BalancesBreakdown]] = None

    feature: Optional[BalancesFeature] = None

    rollovers: Optional[List[BalancesRollover]] = None


class SubscriptionPlanFeaturePriceTier(BaseModel):
    amount: float

    to: Union[float, Literal["inf"]]


class SubscriptionPlanFeaturePrice(BaseModel):
    billing_units: float

    interval: Literal["one_off", "week", "month", "quarter", "semi_annual", "year"]

    max_purchase: Optional[float] = None

    usage_model: Literal["prepaid", "pay_per_use"]

    amount: Optional[float] = None

    interval_count: Optional[float] = None

    tiers: Optional[List[SubscriptionPlanFeaturePriceTier]] = None


class SubscriptionPlanFeatureReset(BaseModel):
    interval: Literal["one_off", "minute", "hour", "day", "week", "month", "quarter", "semi_annual", "year"]

    reset_when_enabled: bool

    interval_count: Optional[float] = None


class SubscriptionPlanFeatureDisplay(BaseModel):
    primary_text: str

    secondary_text: Optional[str] = None


class SubscriptionPlanFeatureFeatureCreditSchema(BaseModel):
    credit_cost: float
    """The credit cost of the metered feature."""

    metered_feature_id: str
    """The ID of the metered feature (should be a single_use feature)."""


class SubscriptionPlanFeatureFeatureDisplay(BaseModel):
    plural: str
    """The plural display name for the feature."""

    singular: str
    """The singular display name for the feature."""


class SubscriptionPlanFeatureFeature(BaseModel):
    id: str
    """
    The ID of the feature, used to refer to it in other API calls like /track or
    /check.
    """

    type: Literal["static", "boolean", "single_use", "continuous_use", "credit_system"]
    """The type of the feature"""

    archived: Optional[bool] = None
    """Whether or not the feature is archived."""

    credit_schema: Optional[List[SubscriptionPlanFeatureFeatureCreditSchema]] = None
    """Credit cost schema for credit system features."""

    display: Optional[SubscriptionPlanFeatureFeatureDisplay] = None
    """Singular and plural display names for the feature."""

    name: Optional[str] = None
    """The name of the feature."""


class SubscriptionPlanFeatureProration(BaseModel):
    on_decrease: Optional[Literal["prorate", "prorate_immediately", "prorate_next_cycle", "none", "no_prorations"]] = (
        None
    )

    on_increase: Optional[
        Literal["bill_immediately", "prorate_immediately", "prorate_next_cycle", "bill_next_cycle"]
    ] = None


class SubscriptionPlanFeatureRollover(BaseModel):
    expiry_duration_type: Literal["month", "forever"]

    max: Optional[float] = None

    expiry_duration_length: Optional[float] = None


class SubscriptionPlanFeature(BaseModel):
    feature_id: str

    granted_balance: float

    price: Optional[SubscriptionPlanFeaturePrice] = None

    reset: Optional[SubscriptionPlanFeatureReset] = None

    unlimited: bool

    display: Optional[SubscriptionPlanFeatureDisplay] = None

    feature: Optional[SubscriptionPlanFeatureFeature] = None

    proration: Optional[SubscriptionPlanFeatureProration] = None

    rollover: Optional[SubscriptionPlanFeatureRollover] = None


class SubscriptionPlanPriceDisplay(BaseModel):
    primary_text: str

    secondary_text: Optional[str] = None


class SubscriptionPlanPrice(BaseModel):
    amount: float

    interval: Literal["one_off", "week", "month", "quarter", "semi_annual", "year"]

    display: Optional[SubscriptionPlanPriceDisplay] = None

    interval_count: Optional[float] = None


class SubscriptionPlanCustomerEligibility(BaseModel):
    scenario: Literal["scheduled", "active", "new", "renew", "upgrade", "downgrade", "cancel", "expired", "past_due"]

    trial_available: Optional[bool] = None


class SubscriptionPlanFreeTrial(BaseModel):
    card_required: bool

    duration_length: float

    duration_type: Literal["day", "month", "year"]


class SubscriptionPlan(BaseModel):
    id: str

    add_on: bool

    archived: bool

    base_variant_id: Optional[str] = None

    created_at: float

    default: bool

    description: Optional[str] = None

    env: Literal["sandbox", "live"]

    features: List[SubscriptionPlanFeature]

    group: Optional[str] = None

    name: str

    price: Optional[SubscriptionPlanPrice] = None

    version: float

    customer_eligibility: Optional[SubscriptionPlanCustomerEligibility] = None

    free_trial: Optional[SubscriptionPlanFreeTrial] = None


class Subscription(BaseModel):
    add_on: bool

    canceled_at: Optional[float] = None

    current_period_end: Optional[float] = None

    current_period_start: Optional[float] = None

    default: bool

    expires_at: Optional[float] = None

    past_due: bool

    plan_id: str

    quantity: float

    started_at: float

    status: Literal["active", "scheduled", "expired"]

    trial_ends_at: Optional[float] = None

    plan: Optional[SubscriptionPlan] = None


class Entity(BaseModel):
    id: Optional[str] = None
    """The unique identifier of the entity"""

    created_at: float
    """Unix timestamp when the entity was created"""

    env: Literal["sandbox", "live"]
    """The environment (sandbox/live)"""

    name: Optional[str] = None
    """The name of the entity"""

    autumn_id: Optional[str] = None

    customer_id: Optional[str] = None
    """The customer ID this entity belongs to"""

    feature_id: Optional[str] = None
    """The feature ID this entity belongs to"""


class Invoice(BaseModel):
    created_at: float
    """Timestamp when the invoice was created"""

    currency: str
    """The currency code for the invoice"""

    product_ids: List[str]
    """Array of product IDs included in this invoice"""

    status: str
    """The status of the invoice"""

    stripe_id: str
    """The Stripe invoice ID"""

    total: float
    """The total amount of the invoice"""

    hosted_invoice_url: Optional[str] = None
    """URL to the Stripe-hosted invoice page"""


class ReferralCustomer(BaseModel):
    id: str

    email: Optional[str] = None

    name: Optional[str] = None


class Referral(BaseModel):
    created_at: float

    customer: ReferralCustomer

    program_id: str

    reward_applied: bool


class RewardsDiscount(BaseModel):
    id: str
    """The unique identifier for this discount"""

    discount_value: float
    """The discount value (percentage or fixed amount)"""

    duration_type: Literal["one_off", "months", "forever"]
    """How long the discount lasts"""

    name: str
    """The name of the discount or coupon"""

    type: Literal["percentage_discount", "fixed_discount", "free_product", "invoice_credits"]
    """The type of reward"""

    currency: Optional[str] = None
    """The currency code for fixed amount discounts"""

    duration_value: Optional[float] = None
    """Number of billing periods the discount applies for repeating durations"""

    end: Optional[float] = None
    """Timestamp when the discount expires"""

    start: Optional[float] = None
    """Timestamp when the discount becomes active"""

    subscription_id: Optional[str] = None
    """The Stripe subscription ID this discount is applied to"""

    total_discount_amount: Optional[float] = None
    """Total amount saved from this discount"""


class Rewards(BaseModel):
    discounts: List[RewardsDiscount]
    """Array of active discounts applied to the customer"""


class TrialsUsed(BaseModel):
    customer_id: str

    product_id: str

    fingerprint: Optional[str] = None


class UpcomingInvoiceDiscount(BaseModel):
    id: str
    """The unique identifier for this discount"""

    discount_value: float
    """The discount value (percentage or fixed amount)"""

    duration_type: Literal["one_off", "months", "forever"]
    """How long the discount lasts"""

    name: str
    """The name of the discount or coupon"""

    type: Literal["percentage_discount", "fixed_discount", "free_product", "invoice_credits"]
    """The type of reward"""

    currency: Optional[str] = None
    """The currency code for fixed amount discounts"""

    duration_value: Optional[float] = None
    """Number of billing periods the discount applies for repeating durations"""

    end: Optional[float] = None
    """Timestamp when the discount expires"""

    start: Optional[float] = None
    """Timestamp when the discount becomes active"""

    subscription_id: Optional[str] = None
    """The Stripe subscription ID this discount is applied to"""

    total_discount_amount: Optional[float] = None
    """Total amount saved from this discount"""


class UpcomingInvoiceLine(BaseModel):
    amount: float

    description: str

    product_id: Optional[str] = None


class UpcomingInvoice(BaseModel):
    currency: str

    discounts: List[UpcomingInvoiceDiscount]

    lines: List[UpcomingInvoiceLine]

    subtotal: float

    total: float


class Customer(BaseModel):
    id: Optional[str] = None

    balances: Dict[str, Balances]

    created_at: float

    email: Optional[str] = None

    env: Literal["sandbox", "live"]

    fingerprint: Optional[str] = None

    metadata: Dict[str, object]

    name: Optional[str] = None

    stripe_id: Optional[str] = None

    subscriptions: List[Subscription]

    autumn_id: Optional[str] = None

    entities: Optional[List[Entity]] = None

    invoices: Optional[List[Invoice]] = None

    payment_method: Optional[object] = None

    referrals: Optional[List[Referral]] = None

    rewards: Optional[Rewards] = None

    trials_used: Optional[List[TrialsUsed]] = None

    upcoming_invoice: Optional[UpcomingInvoice] = None
