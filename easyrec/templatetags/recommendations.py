from easyrec.utils import get_gateway

from django import template
from django.apps import apps
import logging
logger = logging.getLogger(__name__)
from datetime import date 

Product = apps.get_model('catalogue', 'Product')

easyrec = get_gateway()

register = template.Library()

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

@register.simple_tag
def user_recommendations(
    rec_type,
    user,
    product,
    max_results=None,
    requested_item_type=None,
    action_type=None,
    recommendation_type=None
    ):
    """
    Usage: {% user_recommendations [rec_type] [user] [product] as [var] %}

    Sets [var] to contain a list of recommended titles
    for the passed in user

    [rec_type] is the type of the recommendation algorithm, either (Q)uantum or (T)raditional
    """
    logging.debug('user_recommendations: rec_type: %s, user: %s, product: %s' % (rec_type, user, product))
    if not user.is_authenticated:
        return Product.objects.none()

    if (user.demographics):
        birth_date = user.demographics.birth_date
        age = calculate_age(birth_date)

    if action_type:
        action_type = action_type.upper()

    if recommendation_type:
        recommendation_type = recommendation_type.upper()

    category_list = product.get_categories().all()
    category_names = ""
    for cat in category_list:
        category_names += str(cat) + "||"
    if (len(category_names) > 0):
        category_names = category_names[:-2]

    try:
        return easyrec.get_user_recommendations(
            rec_type,
            user.id,
            age,
            user.demographics.gender,
            user.demographics.school_level,
            product.upc,
            category_names,
            max_results,
            requested_item_type,
            action_type,
            recommendation_type
        )
    except Exception as exc:
        logging.warning('user_recommendations: exception: %s', exc)
        return Product.objects.none()


@register.simple_tag
def users_also_bought(
        product,
        user=None,
        max_results=None,
        requested_item_type=None
    ):
    """
    Usage: {% users_also_bought [product] [user] as [var] %}

    Sets [var] to contain a list of products which others who
    have bought [product] have also bought
    """
    user_id = None
    if user:
        user_id = user.id
    try:
        return easyrec.get_other_users_also_bought(
            product.upc,
            user_id,
            max_results,
            product.get_product_class().name,
            requested_item_type
        )
    except:
        return Product.objects.none()


@register.simple_tag
def users_also_viewed(
        product,
        user=None,
        max_results=None,
        requested_item_type=None
    ):
    """
    Usage: {% users_also_viewed [product] [user] as [var] %}

    Sets [var] to contain a list of products which others who
    have viewed [product] have also viewed
    """
    user_id = None
    if user:
        user_id = user.id

    try:
        return easyrec.get_other_users_also_viewed(
            product.upc,
            user_id,
            max_results,
            product.get_product_class().name,
            requested_item_type
        )
    except:
        return Product.objects.none()


@register.simple_tag
def products_rated_good(
        product,
        user=None,
        max_results=None,
        requested_item_type=None
    ):
    user_id = None
    if user:
        user_id = user.id
    try:
        return easyrec.get_items_rated_as_good_by_other_users(
            product.upc,
            user_id,
            max_results,
            product.get_product_class().name,
            requested_item_type
        )
    except:
        return Product.objects.none()


@register.simple_tag
def related_products(
        product,
        max_results=None,
        assoc_type=None,
        requested_item_type=None
    ):
    """
    Usage: {% related_items [product] as [var] %}

    Sets [var] to a list of products related to that specified by [product]
    """
    return easyrec.get_related_items(
        product.upc,
        max_results,
        assoc_type,
        requested_item_type
    )
