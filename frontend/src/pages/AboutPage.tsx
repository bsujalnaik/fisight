  // src/pages/AboutPage.tsx
  import React from "react";

  const AboutPage = () => {
    return (
      <div className="min-h-screen bg-gradient-to-br from-zinc-900 via-zinc-950 to-indigo-950 p-0 md:p-8 flex flex-col items-center font-sans pb-32 md:pb-16">
        <div className="w-full max-w-7xl rounded-none md:rounded-2xl shadow-2xl bg-white/10 backdrop-blur-md border border-zinc-800 p-0 md:p-8 mt-0 md:mt-8 min-h-screen md:min-h-0">
          <div className="w-full flex flex-col items-center mb-6 mt-2">
            <h1 className="text-3xl md:text-4xl font-bold text-white mb-1 drop-shadow-lg">About FinSight</h1>
            <p className="text-zinc-300 text-base md:text-lg">Your AI-powered investment advisor.</p>
          </div>
          <div className="space-y-6 md:space-y-8 p-4 md:p-0 mb-8 md:mb-12">
            <div className="bg-zinc-900 rounded-2xl shadow-md p-6 border border-zinc-800">
              <h2 className="text-2xl font-bold text-white mb-4">Our Mission</h2>
              <p className="text-zinc-300 mb-4">
                FinSight is an AI-powered investment platform designed to help you make informed financial decisions. 
                We combine advanced analytics, real-time market data, and personalized insights to guide your investment journey.
              </p>
              <p className="text-zinc-300 mb-4">
                Whether you're a seasoned investor or just starting out, our intelligent assistant provides 
                comprehensive analysis, portfolio optimization, and tax-efficient strategies tailored to your goals.
              </p>
            </div>``
            
            <div className="bg-zinc-900 rounded-2xl shadow-md p-6 border border-zinc-800">
              <h2 className="text-2xl font-bold text-white mb-4">Key Features</h2>
              <ul className="text-zinc-300 space-y-2">
                <li>• AI-powered investment recommendations</li>
                <li>• Real-time portfolio tracking and analytics</li>
                <li>• Tax optimization strategies</li>
                <li>• Advanced charting and technical analysis</li>
                <li>• Personalized alerts and notifications</li>
                <li>• Comprehensive financial insights</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  };

  export default AboutPage;
