import api from './api';

class OrderService {
  async createOrder(data: any) {
    const response = await api.post('/orders/', data);
    return response.data;
  }
}

export default new OrderService();
