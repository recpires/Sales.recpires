import { FC } from 'react';
import { Modal } from 'antd';
import { ExclamationCircleOutlined } from '@ant-design/icons';

interface ConfirmDeleteModalProps {
  isOpen: boolean;
  productName: string;
  onConfirm: () => void;
  onCancel: () => void;
  loading?: boolean;
}

export const ConfirmDeleteModal: FC<ConfirmDeleteModalProps> = ({
  isOpen,
  productName,
  onConfirm,
  onCancel,
  loading = false,
}) => {
  return (
    <Modal
      title={
        <div className="flex items-center gap-2">
          <ExclamationCircleOutlined className="text-red-500" />
          <span>Confirmar exclusão</span>
        </div>
      }
      open={isOpen}
      onOk={onConfirm}
      onCancel={onCancel}
      okText="Excluir"
      cancelText="Cancelar"
      okButtonProps={{ danger: true, loading }}
      centered
    >
      <p className="text-base mt-4">
        Tem certeza que deseja excluir o produto <strong>"{productName}"</strong>?
      </p>
      <p className="text-sm text-gray-500 mt-2">
        Esta ação não poderá ser desfeita.
      </p>
    </Modal>
  );
};

export default ConfirmDeleteModal;
