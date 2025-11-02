import { useState } from "react";
import { Card, Row, Col, Statistic, Select, DatePicker, Space } from "antd";
import {
  ArrowUpOutlined,
  ShoppingOutlined,
  UserOutlined,
  DollarOutlined,
  RiseOutlined,
} from "@ant-design/icons";
import { NavBar } from "../components/navbar";
import { Aside } from "../components/aside";
import authService from "../services/authService";

const { RangePicker } = DatePicker;

const ReportsPage = () => {
  const user = authService.getCurrentUser();
  const [isAsideOpen, setIsAsideOpen] = useState(true);
  const isAdmin = user?.is_staff || user?.is_superuser;

  const toggleAside = () => {
    setIsAsideOpen(!isAsideOpen);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />

      <div className="flex">
        {isAdmin && <Aside isOpen={isAsideOpen} onToggle={toggleAside} />}

        <main className="flex-1 p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Relatórios
            </h1>
            <p className="text-gray-600">
              Visualize métricas e estatísticas do negócio
            </p>
          </div>

          {/* Filtros */}
          <Card className="mb-6">
            <Space size="middle">
              <Select
                defaultValue="month"
                style={{ width: 150 }}
                options={[
                  { value: "today", label: "Hoje" },
                  { value: "week", label: "Esta Semana" },
                  { value: "month", label: "Este Mês" },
                  { value: "year", label: "Este Ano" },
                ]}
              />
              <RangePicker />
            </Space>
          </Card>

          {/* Métricas Principais */}
          <Row gutter={16} className="mb-8">
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Receita Total"
                  value={112893}
                  precision={2}
                  valueStyle={{ color: "#3f8600" }}
                  prefix={<DollarOutlined />}
                  suffix={
                    <span className="text-sm">
                      <ArrowUpOutlined /> 12.5%
                    </span>
                  }
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Total de Vendas"
                  value={1234}
                  valueStyle={{ color: "#1890ff" }}
                  prefix={<ShoppingOutlined />}
                  suffix={
                    <span className="text-sm">
                      <ArrowUpOutlined /> 8.3%
                    </span>
                  }
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Novos Clientes"
                  value={87}
                  valueStyle={{ color: "#52c41a" }}
                  prefix={<UserOutlined />}
                  suffix={
                    <span className="text-sm">
                      <ArrowUpOutlined /> 15.2%
                    </span>
                  }
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Taxa de Conversão"
                  value={9.3}
                  precision={1}
                  valueStyle={{ color: "#faad14" }}
                  prefix={<RiseOutlined />}
                  suffix="%"
                />
              </Card>
            </Col>
          </Row>

          {/* Gráficos e Análises */}
          <Row gutter={16}>
            <Col xs={24} lg={12}>
              <Card title="Vendas por Período" className="mb-4">
                <div className="h-64 flex items-center justify-center bg-gray-100 rounded">
                  <p className="text-gray-500">Gráfico de vendas por período</p>
                </div>
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card title="Produtos Mais Vendidos" className="mb-4">
                <div className="h-64 flex items-center justify-center bg-gray-100 rounded">
                  <p className="text-gray-500">
                    Gráfico de produtos mais vendidos
                  </p>
                </div>
              </Card>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} lg={12}>
              <Card title="Receita por Categoria" className="mb-4">
                <div className="h-64 flex items-center justify-center bg-gray-100 rounded">
                  <p className="text-gray-500">
                    Gráfico de receita por categoria
                  </p>
                </div>
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card title="Clientes Ativos" className="mb-4">
                <div className="h-64 flex items-center justify-center bg-gray-100 rounded">
                  <p className="text-gray-500">Gráfico de clientes ativos</p>
                </div>
              </Card>
            </Col>
          </Row>
        </main>
      </div>
    </div>
  );
};

export default ReportsPage;
