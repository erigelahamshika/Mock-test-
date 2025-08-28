import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import MockTestCreator from './components/MockTestCreator';
import MockTestGenerator from './components/MockTestGenerator';
import './App.css';

const App = () => {
  const [currentView, setCurrentView] = useState('dashboard');
  const [testData, setTestData] = useState(null);

  const handleCreateTest = () => {
    setCurrentView('creator');
  };

  const handleBackToDashboard = () => {
    setCurrentView('dashboard');
    setTestData(null);
  };

  const handleCreateMockTest = (formData) => {
    setTestData(formData);
    setCurrentView('generator');
  };

  const handleBackToCreator = () => {
    setCurrentView('creator');
  };

  const handleViewReviews = () => {
    // Handle view reviews logic
    console.log('View reviews clicked');
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard':
        return (
          <Dashboard
            onCreateTest={handleCreateTest}
            onViewReviews={handleViewReviews}
          />
        );
      case 'creator':
        return (
          <MockTestCreator
            onBackToDashboard={handleBackToDashboard}
            onCreateMockTest={handleCreateMockTest}
          />
        );
      case 'generator':
        return (
          <MockTestGenerator
            testData={testData}
            onBackToCreator={handleBackToCreator}
          />
        );
      default:
        return <Dashboard onCreateTest={handleCreateTest} />;
    }
  };

  return (
    <div className="app">
      {renderCurrentView()}
    </div>
  );
};

export default App;
