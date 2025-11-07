import React from 'react'


export default function Sidebar({ menuItems, activeView, onChange }) {
    return (
        <div className="bg-white rounded-lg shadow-sm p-2 mb-6 border" style={{ borderColor: '#E0D8CF' }}>
            <div className="flex gap-2">
                {menuItems.map(item => (
                    <button
                        key={item.id}
                        onClick={() => onChange(item.id)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${activeView === item.id ? 'font-medium' : 'hover:bg-gray-50'}`}
                        style={{ backgroundColor: activeView === item.id ? '#D4A574' : 'transparent', color: activeView === item.id ? '#FFFFFF' : '#666' }}
                    >
                        {item.label}
                    </button>
                ))}
            </div>
        </div>
    )
}