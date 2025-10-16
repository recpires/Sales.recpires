import React, { useState } from 'react';
import { api } from '../services/api';

interface RegisterForm {
  name: string;
  email: string;
  password: string;
  passwordConfirm?: string;
}

const RegisterPage: React.FC = () => {
  const [form, setForm] = useState<RegisterForm>({ name: '', email: '', password: '', passwordConfirm: '' });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string[]>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    try {
      const payload = {
        name: form.name,
        email: form.email,
        password: form.password,
      };
      await api.post('/auth/register/', payload);
      // redirecionar após registro, ou mostrar sucesso
      window.location.href = '/login';
    } catch (err: unknown) {
      // tratamento seguro de erro
      const anyErr = err as any;
      if (anyErr?.response?.data) {
        setErrors(anyErr.response.data);
      } else {
        // fallback: log e mostrar mensagem genérica
        console.error('Registration error', err);
        setErrors({ non_field_errors: ['Ocorreu um erro ao registrar. Tente novamente.'] });
      }

      // Evitar acesso inseguro a error.config e headers
      try {
        const cfg = anyErr?.config;
        if (cfg && typeof cfg === 'object') {
          // apenas usar se necessário, por exemplo para debug
          // console.debug('Failed request config', cfg);
        }
      } catch {
        // ignore
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Registrar</h1>
      <form onSubmit={handleSubmit}>
        <input name="name" value={form.name} onChange={handleChange} placeholder="Nome" />
        {errors.name && <div>{(errors.name || []).join(', ')}</div>}
        <input name="email" value={form.email} onChange={handleChange} placeholder="Email" />
        {errors.email && <div>{(errors.email || []).join(', ')}</div>}
        <input name="password" type="password" value={form.password} onChange={handleChange} placeholder="Senha" />
        {errors.password && <div>{(errors.password || []).join(', ')}</div>}
        <button type="submit" disabled={loading}>Registrar</button>
      </form>
    </div>
  );
};

export default RegisterPage;
