import { HTMLAttributes, ReactNode } from 'react';

type CardPadding = 'none' | 'sm' | 'md' | 'lg';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  className?: string;
  padding?: CardPadding;
  shadow?: boolean;
  hover?: boolean;
}

interface CardSubComponentProps {
  children: ReactNode;
  className?: string;
}

const Card = ({
  children,
  className = '',
  padding = 'md',
  shadow = true,
  hover = false,
  ...props
}: CardProps) => {
  const baseStyles = 'bg-white rounded-lg border border-gray-200';

  const paddingStyles: Record<CardPadding, string> = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  const shadowStyles = shadow ? 'shadow-md' : '';
  const hoverStyles = hover ? 'hover:shadow-lg transition-shadow duration-200' : '';

  const cardClasses = `
    ${baseStyles}
    ${paddingStyles[padding]}
    ${shadowStyles}
    ${hoverStyles}
    ${className}
  `.trim().replace(/\s+/g, ' ');

  return (
    <div className={cardClasses} {...props}>
      {children}
    </div>
  );
};

const CardHeader = ({ children, className = '' }: CardSubComponentProps) => (
  <div className={`border-b border-gray-200 pb-4 mb-4 ${className}`}>
    {children}
  </div>
);

const CardTitle = ({ children, className = '' }: CardSubComponentProps) => (
  <h3 className={`text-xl font-semibold text-gray-900 ${className}`}>
    {children}
  </h3>
);

const CardContent = ({ children, className = '' }: CardSubComponentProps) => (
  <div className={className}>
    {children}
  </div>
);

const CardFooter = ({ children, className = '' }: CardSubComponentProps) => (
  <div className={`border-t border-gray-200 pt-4 mt-4 ${className}`}>
    {children}
  </div>
);

type CardComponent = typeof Card & {
  Header: typeof CardHeader;
  Title: typeof CardTitle;
  Content: typeof CardContent;
  Footer: typeof CardFooter;
};

const CardWithSubComponents = Card as CardComponent;

CardWithSubComponents.Header = CardHeader;
CardWithSubComponents.Title = CardTitle;
CardWithSubComponents.Content = CardContent;
CardWithSubComponents.Footer = CardFooter;

export default CardWithSubComponents;
