import React from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import Features from './components/Features';
import HowItWorks from './components/HowItWorks';
import SampleTable from './components/SampleTable';
import WhyUs from './components/WhyUs';
import Footer from './components/Footer';
import './App.css';

function App() {
  return (
    <div className="App bg-gray-50 min-h-screen">
      <Header />
      <main>
        <Hero />
        <Features />
        <HowItWorks />
        <SampleTable />
        <WhyUs />
      </main>
      <Footer />
    </div>
  );
}

export default App;