import React from 'react';

// Loading Spinner
export const LoadingSpinner: React.FC = () => (
  <div className="flex justify-center items-center h-64">
    <div className="spinner"></div>
  </div>
);

// Alert Messages
interface AlertProps {
  message: string;
  type?: 'success' | 'danger' | 'warning' | 'info';
  onDismiss?: () => void;
}

export const Alert: React.FC<AlertProps> = ({ message, type = 'info', onDismiss }) => {
  const alertClass = `alert alert-${type}`;
  return (
    <div className={alertClass}>
      <div className="flex justify-between items-center">
        <span>{message}</span>
        {onDismiss && (
          <button onClick={onDismiss} className="text-lg hover:opacity-80 transition">
            <i className="fas fa-xmark"></i>
          </button>
        )}
      </div>
    </div>
  );
};

export const ErrorMessage: React.FC<{ message: string; onDismiss?: () => void }> = (props) => (
  <Alert type="danger" {...props} />
);

export const SuccessMessage: React.FC<{ message: string; onDismiss?: () => void }> = (props) => (
  <Alert type="success" {...props} />
);

// Button Component
interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning' | 'info';
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  fullWidth?: boolean;
  icon?: string;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  type = 'button',
  variant = 'primary',
  disabled = false,
  loading = false,
  className = '',
  fullWidth = false,
  icon,
}) => {
  const baseClass = `btn-pill bg-${variant} text-white font-medium`;
  const widthClass = fullWidth ? 'w-full' : '';
  const disabledClass = disabled || loading ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-lg';
  
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`${baseClass} ${widthClass} ${disabledClass} ${className}`}
    >
      {loading ? (
        <>
          <span className="spinner inline-block mr-2" style={{ width: '16px', height: '16px' }}></span>
          {children}
        </>
      ) : (
        <>
          {icon && <i className={`fas fa-${icon} mr-2`}></i>}
          {children}
        </>
      )}
    </button>
  );
};

// Card Component
interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  icon?: string;
  footer?: React.ReactNode;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({ children, className = '', title, icon, footer, onClick }) => (
  <div className={`card ${className}`} onClick={onClick} style={{cursor: onClick ? 'pointer' : 'default'}}>
    {(title || icon) && (
      <div className="flex items-center mb-4 pb-4 border-b border-white/10">
        {icon && <i className={`fas fa-${icon} text-2xl text-primary mr-3`}></i>}
        {title && <h3 className="text-lg font-semibold">{title}</h3>}
      </div>
    )}
    {children}
    {footer && <div className="mt-4 pt-4 border-t border-white/10">{footer}</div>}
  </div>
);

// Stats Card
interface StatsCardProps {
  icon: string;
  title: string;
  description?: string;
  onClick?: () => void;
  children?: React.ReactNode;
}

export const StatsCard: React.FC<StatsCardProps> = ({ icon, title, description, onClick, children }) => (
  <Card className="stats-card text-center cursor-pointer" onClick={onClick}>
    <i className={`fas fa-${icon} fa-3x mb-3 text-primary block`}></i>
    <h5 className="card-title text-lg font-semibold mb-2">{title}</h5>
    {description && <p className="card-text text-text-muted mb-4">{description}</p>}
    {children}
  </Card>
);

// Input Component
interface InputProps {
  type?: string;
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  label?: string;
  error?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
  icon?: string;
}

export const Input: React.FC<InputProps> = ({
  type = 'text',
  placeholder,
  value,
  onChange,
  label,
  error,
  required,
  disabled,
  className = '',
  icon,
}) => (
  <div className="mb-4">
    {label && (
      <label className="block text-sm font-medium mb-2 text-text-secondary">
        {label}
        {required && <span className="text-danger ml-1">*</span>}
      </label>
    )}
    <div className="relative">
      {icon && (
        <i className={`fas fa-${icon} absolute left-4 top-3.5 text-text-muted`}></i>
      )}
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
        className={`w-full ${icon ? 'pl-10' : ''} ${error ? 'border-danger' : ''} ${className}`}
      />
    </div>
    {error && <p className="text-danger text-sm mt-1">{error}</p>}
  </div>
);

// Select Component
interface SelectProps {
  options: Array<{ value: string | number; label: string }>;
  value?: string | number;
  onChange?: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  label?: string;
  error?: string;
  required?: boolean;
  className?: string;
}

export const Select: React.FC<SelectProps> = ({
  options,
  value,
  onChange,
  label,
  error,
  required,
  className = '',
}) => (
  <div className="mb-4">
    {label && (
      <label className="block text-sm font-medium mb-2 text-text-secondary">
        {label}
        {required && <span className="text-danger ml-1">*</span>}
      </label>
    )}
    <select
      value={value}
      onChange={onChange}
      className={`w-full ${error ? 'border-danger' : ''} ${className}`}
    >
      <option value="">Select an option</option>
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
    {error && <p className="text-danger text-sm mt-1">{error}</p>}
  </div>
);

// Modal Component
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = 'md',
}) => {
  if (!isOpen) return null;

  const sizeClass = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
  }[size];

  return (
    <div className="modal active">
      <div className={`modal-content ${sizeClass}`}>
        <div className="flex justify-between items-center p-6 border-b border-white/10">
          <h2 className="text-xl font-bold">{title}</h2>
          <button
            onClick={onClose}
            className="text-2xl text-text-muted hover:text-white transition"
          >
            <i className="fas fa-xmark"></i>
          </button>
        </div>
        <div className="p-6">{children}</div>
        {footer && (
          <div className="p-6 border-t border-white/10 flex justify-end space-x-2">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};

// Table Component
interface TableColumn {
  key: string;
  header: string;
  render?: (value: any, row: any) => React.ReactNode;
}

interface TableProps {
  columns: TableColumn[];
  data: any[];
  loading?: boolean;
  onRowClick?: (row: any) => void;
}

export const Table: React.FC<TableProps> = ({ columns, data, loading = false, onRowClick }) => {
  if (loading) return <LoadingSpinner />;

  if (data.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-text-muted">No data available</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key}>{col.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr
              key={idx}
              onClick={() => onRowClick?.(row)}
              className={onRowClick ? 'cursor-pointer' : ''}
            >
              {columns.map((col) => (
                <td key={col.key}>
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Pagination Component
interface PaginationProps {
  page: number;
  limit: number;
  total: number;
  onPageChange: (page: number) => void;
}

export const Pagination: React.FC<PaginationProps> = ({ page, limit, total, onPageChange }) => {
  const totalPages = Math.ceil(total / limit);
  const startItem = (page - 1) * limit + 1;
  const endItem = Math.min(page * limit, total);

  return (
    <div className="flex justify-between items-center mt-6">
      <div className="text-sm text-text-muted">
        Showing {startItem} to {endItem} of {total} results
      </div>
      <div className="flex gap-2">
        <Button
          onClick={() => onPageChange(page - 1)}
          disabled={page === 1}
          variant="secondary"
        >
          Previous
        </Button>
        <span className="px-4 py-2">
          Page {page} of {totalPages}
        </span>
        <Button
          onClick={() => onPageChange(page + 1)}
          disabled={page === totalPages}
          variant="secondary"
        >
          Next
        </Button>
      </div>
    </div>
  );
};
