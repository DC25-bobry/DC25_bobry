import React from 'react'


export default function Footer() {
    return (
        <footer className="border-t mt-12 py-6" style={{ backgroundColor: '#FFFFFF', borderColor: '#E0D8CF' }}>
            <div className="max-w-7xl mx-auto px-6 text-center">
                <p style={{ color: '#666' }}>
                    <br/>
                    Bóbrpol sp. k. © 2025 Wszelkie prawa zastrzeżone
                    <br/>
                </p>
                <div className="flex justify-center gap-8 mt-4 text-3xl">
                    <img src="./src/assets/bobr.gif" alt="bober" className="img-fixed"></img>
                    <img src="./src/assets/bobr.gif" alt="bober" className="img-fixed"></img>
                    <img src="./src/assets/bobr.gif" alt="bober" className="img-fixed"></img>
                </div>
                <br/>
            </div>
        </footer>
    )
}