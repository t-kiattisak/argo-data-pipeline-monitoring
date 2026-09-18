CREATE TABLE IF NOT EXISTS iot_device_events (
    id UUID PRIMARY KEY,
    payload JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'PROCESSED',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS store_order_events (
    id VARCHAR(50) PRIMARY KEY,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Seed Sample Demo Data
INSERT INTO iot_device_events (id, payload, created_at)
VALUES 
    (
        'a1111111-1111-1111-1111-111111111111',
        '{
            "device_id": "DEV-BKK-001",
            "battery_level": 94.5,
            "temperature_c": 28.4,
            "firmware_version": "v2.4.1",
            "signal_strength_dbm": -65,
            "cpu_usage_pct": 14.2,
            "memory_usage_pct": 45.8,
            "operating_mode": "ACTIVE",
            "network_type": "5G",
            "ip_address": "192.168.1.10"
        }',
        CURRENT_DATE - INTERVAL '1 day' + TIME '10:15:00'
    ),
    (
        'b2222222-2222-2222-2222-222222222222',
        '{
            "device_id": "DEV-CNX-002",
            "battery_level": 78.0,
            "temperature_c": 31.2,
            "firmware_version": "v2.4.1",
            "signal_strength_dbm": -72,
            "cpu_usage_pct": 28.5,
            "memory_usage_pct": 52.1,
            "operating_mode": "ACTIVE",
            "network_type": "WIFI",
            "ip_address": "192.168.1.11"
        }',
        CURRENT_DATE - INTERVAL '1 day' + TIME '14:20:00'
    );

INSERT INTO store_order_events (id, payload, created_at)
VALUES 
    (
        'ORD-2026-9001',
        '{
            "customer_id": "CUST-9901",
            "event_type": "ORDER_PLACED",
            "currency": "THB",
            "total_amount": 2500.00,
            "discount_amount": 250.00,
            "item_count": 3,
            "payment_method": "PROMPTPAY",
            "shipping_carrier": "KERRY",
            "delivery_country": "TH"
        }',
        CURRENT_DATE - INTERVAL '1 day' + TIME '11:00:00'
    ),
    (
        'ORD-2026-9002',
        '{
            "customer_id": "CUST-9902",
            "event_type": "ORDER_COMPLETED",
            "currency": "THB",
            "total_amount": 1150.50,
            "discount_amount": 0.00,
            "item_count": 1,
            "payment_method": "CREDIT_CARD",
            "shipping_carrier": "FLASH",
            "delivery_country": "TH"
        }',
        CURRENT_DATE - INTERVAL '1 day' + TIME '16:45:00'
    );
