package org.fffd.l23o6.util.strategy.payment;

import org.fffd.l23o6.pojo.entity.OrderEntity;

public abstract class PaymentStrategy {

    public  abstract boolean pay(OrderEntity order);
    public  abstract boolean refund(OrderEntity order);
}
