import { InputHTMLAttributes } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

const Input = ({
  label,
  type = 'text',
  placeholder = '',
  error,
  helperText,
  className = '',
  disabled = false,
  required = false,
  ...props
}: InputProps) => {
  const baseStyles = 'w-full px-4 py-2 border rounded-lg transition-all duration-200 focus:outline-none focus:ring-2';
  const normalStyles = 'border-gray-300 focus:ring-blue-500 focus:border-blue-500';
  const errorStyles = 'border-red-500 focus:ring-red-500 focus:border-red-500';
  const disabledStyles = 'bg-gray-100 cursor-not-allowed';

  const inputClasses = `
    ${baseStyles}
    ${error ? errorStyles : normalStyles}
    ${disabled ? disabledStyles : ''}
    ${className}
  `.trim().replace(/\s+/g, ' ');

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <input
        type={type}
        className={inputClasses}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
      {helperText && !error && (
        <p className="mt-1 text-sm text-gray-500">{helperText}</p>
      )}
    </div>
  );
};

export default Input;
