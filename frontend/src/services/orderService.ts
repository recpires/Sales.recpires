import api from './api';

class OrderService {
  async createOrder(data: any) {
    const response = await api.post('/orders/', data);
    return response.data;
  }

  async getOrders() {
    const response = await api.get('/orders/');
    return response.data;
  }

  async getOrderById(id: number) {
    const response = await api.get(`/orders/${id}/`);
    return response.data;
  }

  async updateOrderStatus(id: number, status: string) {
    const response = await api.post(`/orders/${id}/update_status/`, { status });
    return response.data;
  }
}

export default new OrderService();
