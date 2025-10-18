import axios from 'axios';

export interface CepData {
  cep: string;
  logradouro: string;
  complemento: string;
  bairro: string;
  localidade: string;
  uf: string;
  erro?: boolean;
}

class CepService {
  /**
   * Busca informações de endereço pelo CEP usando a API ViaCEP
   */
  async fetchAddress(cep: string): Promise<CepData> {
    // Remove caracteres não numéricos
    const cleanCep = cep.replace(/\D/g, '');

    if (cleanCep.length !== 8) {
      throw new Error('CEP deve conter 8 dígitos');
    }

    try {
      const response = await axios.get(`https://viacep.com.br/ws/${cleanCep}/json/`);

      if (response.data.erro) {
        throw new Error('CEP não encontrado');
      }

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error('Erro ao consultar CEP. Verifique sua conexão.');
      }
      throw error;
    }
  }

  /**
   * Calcula o frete com base no CEP
   * Simulação simples baseada na região
   */
  calculateShipping(cep: string, subtotal: number): { value: number; days: number; type: string } {
    const cleanCep = cep.replace(/\D/g, '');
    const region = parseInt(cleanCep.substring(0, 1));

    // Frete grátis para compras acima de R$ 200
    if (subtotal >= 200) {
      return {
        value: 0,
        days: 5,
        type: 'Frete Grátis',
      };
    }

    // Calcula frete por região do Brasil
    // Região 0-3: Sudeste/Sul (mais barato)
    // Região 4-5: Centro-Oeste (médio)
    // Região 6-9: Norte/Nordeste (mais caro)
    let baseShipping = 0;
    let days = 0;

    if (region >= 0 && region <= 3) {
      baseShipping = 15;
      days = 5;
    } else if (region >= 4 && region <= 5) {
      baseShipping = 25;
      days = 7;
    } else {
      baseShipping = 35;
      days = 10;
    }

    return {
      value: baseShipping,
      days,
      type: 'PAC',
    };
  }

  /**
   * Formata CEP para exibição (00000-000)
   */
  formatCep(cep: string): string {
    const cleanCep = cep.replace(/\D/g, '');
    return cleanCep.replace(/(\d{5})(\d{3})/, '$1-$2');
  }
}

export default new CepService();
