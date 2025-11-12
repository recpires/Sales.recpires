import React from "react";
import { Alert } from "antd";
import { getApiErrors } from "../../services/errorUtils";

interface Props {
  error: any;
}

const ApiErrorAlert: React.FC<Props> = ({ error }) => {
  const apiErrors = getApiErrors(error);
  if (!apiErrors) return null;

  // ---
  // Caso 1: O erro é um array de mensagens (Ex: ["Erro 1", "Erro 2"])
  // ---
  if (Array.isArray(apiErrors)) {
    const messages = apiErrors.map((msg, index) => (
      <li key={index}>{String(msg)}</li>
    ));

    return (
      <Alert
        type="error"
        message="Ocorreram os seguintes erros:"
        description={<ul>{messages}</ul>}
        className="mb-4" // Adiciona um espaçamento (opcional)
      />
    );
  }

  // ---
  // Caso 2: O erro é um objeto de campos (Ex: { name: "...", email: "..." })
  // ---
  if (typeof apiErrors === "object" && !Array.isArray(apiErrors)) {
    const messages = Object.entries(apiErrors).map(([field, errorValue]) => {
      // Garante que o valor do erro seja tratado como array
      const errorList = Array.isArray(errorValue) ? errorValue : [errorValue];

      return (
        <li key={field}>
          <strong>{field}:</strong> {errorList.join(", ")}
        </li>
      );
    });

    return (
      <Alert
        type="error"
        message="Por favor, corrija os erros no formulário:"
        description={<ul>{messages}</ul>}
        className="mb-4"
      />
    );
  }

  // ---
  // Caso 3: O erro é uma string simples (Fallback)
  // ---
  return <Alert type="error" message={String(apiErrors)} className="mb-4" />;
};

export default ApiErrorAlert;
