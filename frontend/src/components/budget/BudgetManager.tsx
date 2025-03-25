import React, { useState } from 'react';
import BudgetList from './BudgetList';
import BudgetForm from './BudgetForm';
import BudgetDetail from './BudgetDetail';

enum BudgetView {
  LIST,
  CREATE,
  DETAIL
}

export default function BudgetManager() {
  const [currentView, setCurrentView] = useState<BudgetView>(BudgetView.LIST);
  const [selectedBudgetId, setSelectedBudgetId] = useState<number | null>(null);

  const handleSelectBudget = (budgetId: number) => {
    setSelectedBudgetId(budgetId);
    setCurrentView(BudgetView.DETAIL);
  };

  const handleCreateBudget = () => {
    setCurrentView(BudgetView.CREATE);
  };

  const handleBudgetCreated = () => {
    setCurrentView(BudgetView.LIST);
  };

  const handleBackToList = () => {
    setCurrentView(BudgetView.LIST);
    setSelectedBudgetId(null);
  };

  const renderView = () => {
    switch (currentView) {
      case BudgetView.LIST:
        return (
          <BudgetList 
            onSelectBudget={handleSelectBudget} 
            onCreateBudget={handleCreateBudget}
          />
        );
      case BudgetView.CREATE:
        return (
          <BudgetForm
            onSave={handleBudgetCreated}
            onCancel={handleBackToList}
          />
        );
      case BudgetView.DETAIL:
        if (selectedBudgetId) {
          return (
            <BudgetDetail
              budgetId={selectedBudgetId}
              onBack={handleBackToList}
              onRefresh={() => {}}
            />
          );
        }
        return <div>Error: No se seleccionó ningún presupuesto.</div>;
      default:
        return <div>Vista no válida.</div>;
    }
  };

  return (
    <div className="budget-manager">
      {renderView()}
      
      <style jsx>{`
        .budget-manager {
          width: 100%;
        }
      `}</style>
    </div>
  );
}
