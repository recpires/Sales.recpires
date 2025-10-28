{state.items.map((item) => {
                    const product = item.product;
                    const variant = product?.variants?.find((v) => v.id === item.variantId) ?? null;
                    // CORREÇÃO: Preço SÓ PODE VIR DA VARIANTE
                    const unitPrice = variant ? Number(variant.price) : 0; // Se não achar, preço é 0 (indica erro no estado)

                    return (
                      <div key={`${item.productId}-${item.variantId}`} /* ... restante do JSX ... */ >
                        {/* ... */}
                        <div className="flex justify-between mt-1">
                          <Text type="secondary" className="text-xs">Qtd: {item.quantity}</Text>
                          <Text strong className="text-sm">R$ {(unitPrice * item.quantity).toFixed(2)}</Text> {/* Usa unitPrice corrigido */}
                        </div>
                      {/* ... */}
                      </div>
                    );
                  })}