import { useState } from 'react';
import LoginPage from './pages/LoginPage';
import Layout from './components/layout/Layout';
import { Button, Card, Input, Badge } from './components/common';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [inputValue, setInputValue] = useState<string>('');
  const [count, setCount] = useState<number>(0);

  const handleLogin = (email: string, password: string) => {
    console.log('Login attempt:', { email, password });
    // Aqui você pode adicionar a lógica de autenticação real
    setIsLoggedIn(true);
  };

  if (!isLoggedIn) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <Layout>
      <div className="space-y-8">
        {/* Hero Section */}
        <div className="text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Welcome to Sales Dashboard
          </h2>
          <p className="text-lg text-gray-600 mb-6">
            Built with React, Vite, and Tailwind CSS
          </p>
          <div className="flex justify-center gap-2">
            <Badge variant="primary">React 19</Badge>
            <Badge variant="success">Tailwind CSS</Badge>
            <Badge variant="info">Vite</Badge>
          </div>
        </div>

        {/* Components Showcase */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Buttons Card */}
          <Card>
            <Card.Header>
              <Card.Title>Buttons</Card.Title>
            </Card.Header>
            <Card.Content>
              <div className="space-y-3">
                <div className="flex flex-wrap gap-2">
                  <Button variant="primary" size="sm">Primary Small</Button>
                  <Button variant="primary">Primary</Button>
                  <Button variant="primary" size="lg">Primary Large</Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button variant="secondary">Secondary</Button>
                  <Button variant="outline">Outline</Button>
                  <Button variant="danger">Danger</Button>
                  <Button variant="success">Success</Button>
                </div>
                <div>
                  <Button disabled>Disabled</Button>
                </div>
              </div>
            </Card.Content>
          </Card>

          {/* Counter Card */}
          <Card hover>
            <Card.Header>
              <Card.Title>Interactive Counter</Card.Title>
            </Card.Header>
            <Card.Content>
              <div className="text-center space-y-4">
                <div className="text-5xl font-bold text-blue-600">{count}</div>
                <div className="flex justify-center gap-2">
                  <Button
                    variant="danger"
                    onClick={() => setCount(count - 1)}
                  >
                    Decrement
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={() => setCount(0)}
                  >
                    Reset
                  </Button>
                  <Button
                    variant="success"
                    onClick={() => setCount(count + 1)}
                  >
                    Increment
                  </Button>
                </div>
              </div>
            </Card.Content>
          </Card>

          {/* Input Card */}
          <Card>
            <Card.Header>
              <Card.Title>Form Inputs</Card.Title>
            </Card.Header>
            <Card.Content>
              <div className="space-y-4">
                <Input
                  label="Email Address"
                  type="email"
                  placeholder="Enter your email"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  helperText="We'll never share your email with anyone else."
                />
                <Input
                  label="Password"
                  type="password"
                  placeholder="Enter password"
                  required
                />
                <Input
                  label="Error State"
                  placeholder="This field has an error"
                  error="This field is required"
                />
                <Input
                  label="Disabled Input"
                  placeholder="This is disabled"
                  disabled
                />
              </div>
            </Card.Content>
          </Card>

          {/* Badges Card */}
          <Card>
            <Card.Header>
              <Card.Title>Badges & Status</Card.Title>
            </Card.Header>
            <Card.Content>
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  <Badge variant="default">Default</Badge>
                  <Badge variant="primary">Primary</Badge>
                  <Badge variant="success">Success</Badge>
                  <Badge variant="warning">Warning</Badge>
                  <Badge variant="danger">Danger</Badge>
                  <Badge variant="info">Info</Badge>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Badge size="sm">Small</Badge>
                  <Badge size="md">Medium</Badge>
                  <Badge size="lg">Large</Badge>
                </div>
              </div>
            </Card.Content>
            <Card.Footer>
              <p className="text-sm text-gray-600">
                Use badges to highlight status, categories, or notifications
              </p>
            </Card.Footer>
          </Card>
        </div>

        {/* Full Width Card */}
        <Card padding="lg">
          <Card.Header>
            <Card.Title>Getting Started</Card.Title>
          </Card.Header>
          <Card.Content>
            <div className="prose max-w-none">
              <p className="text-gray-600 mb-4">
                This is a fully configured React application with Tailwind CSS and reusable components.
                All components are located in <code className="bg-gray-100 px-2 py-1 rounded">src/components/</code>.
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-600">
                <li>Button component with multiple variants and sizes</li>
                <li>Card component with header, content, and footer sections</li>
                <li>Input component with label, error states, and helper text</li>
                <li>Badge component for status indicators</li>
                <li>Layout component with header and footer</li>
              </ul>
            </div>
          </Card.Content>
        </Card>

        {/* Logout Button */}
        <div className="text-center">
          <Button
            variant="outline"
            onClick={() => setIsLoggedIn(false)}
          >
            Sair
          </Button>
        </div>
      </div>
    </Layout>
  );
}

export default App;
