DOMAIN = "amazon_order_status"

CONF_EMAIL = "email"
CONF_IMAP_SERVER = "imap_server"
CONF_IMAP_PORT = "imap_port"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_POLL_INTERVAL = "poll_interval"
CONF_MARK_AS_READ = "mark_as_read"
CONF_DELIVERED_RETENTION_DAYS = "delivered_retention_days"
CONF_CANCELLED_RETENTION_DAYS = "cancelled_retention_days"
CONF_IMAP_FOLDER = "imap_folder"
ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_INVALID_AUTH = "invalid_auth"

SERVICE_PURGE_ORDER = "purge_order"
SERVICE_RESCAN = "rescan"
ATTR_ORDER_ID = "order_id"
ATTR_DAYS = "days"

# Fired when an order stops being an active shipment, so automations can tear
# down anything they created for it (Live Activities, persistent notifications).
EVENT_ORDER_CANCELLED = "amazon_order_status_order_cancelled"
EVENT_ORDER_REMOVED = "amazon_order_status_order_removed"

STATUS_CANCELLED = "Cancelled"
STATUS_DELIVERED = "Delivered"

DEFAULT_POLL_INTERVAL = 1800  # 30 minutes
DEFAULT_CANCELLED_RETENTION_DAYS = 1
