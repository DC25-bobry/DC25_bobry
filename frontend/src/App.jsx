import React, { useState } from 'react'
import Header from './components/Layout/Header'
import Sidebar from './components/Layout/Sidebar'
import Footer from './components/Layout/Footer'
import JobOffersPage from './pages/JobOffersPage'
import CandidatesPage from './pages/CandidatesPage'
import CVPage from './pages/CVPage'


const menuItems = [
    { id: 'jobs', label: 'Oferty Pracy' },
    { id: 'cv', label: 'CV' },
    { id: 'candidates', label: 'Kandydaci' },
]


export default function App() {
    const [activeView, setActiveView] = useState('jobs')


    return (
        <div className="min-h-screen" style={{ backgroundColor: '#F5F1ED' }}>
            <Header />


            <div className="max-w-7xl mx-auto px-6 py-6">
                <Sidebar
                    menuItems={menuItems}
                    activeView={activeView}
                    onChange={setActiveView}
                />


                <main className="mt-6">
                    {activeView === 'dashboard' && <Dashboard />}
                    {activeView === 'jobs' && <JobOffersPage />}
                    {activeView === 'candidates' && <CandidatesPage />}
                    {activeView === 'cv' && <CVPage />}
                </main>
            </div>


            <Footer />
        </div>
    )
}