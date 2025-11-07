import React from 'react'

export default function Header() {
    return (
        <header
            className="border-b-2"
            style={{ backgroundColor: '#FFFFFF', borderColor: '#8B6F47' }}
        >
            <div className="max-w-7xl mx-auto px-6 py-4">
                <div className="grid grid-cols-3 items-center">

                    <div className="flex items-center gap-2">
                        <img src="./src/assets/bobr.gif" alt="bober" className="img-fixed"></img>
                        <img src="./src/assets/bobr.gif" alt="bober" className="img-fixed"></img>
                        <img src="./src/assets/bobr.gif" alt="bober" className="img-fixed"></img>
                        <img src="./src/assets/bobr.gif" alt="bober" className="img-fixed"></img>
                        <img src="./src/assets/bobr.gif" alt="bober" className="img-fixed"></img>
                    </div>

                    <div className="flex flex-col items-center text-center">
                        <div className="flex items-center gap-3 justify-center">
                            <img src="./src/assets/bobr.webp" alt="bober" className="img-fixed"></img>
                            <div>
                                <h1 className="text-2xl font-bold" style={{ color: '#8B6F47' }}>
                                    BóbrPol sp. k.
                                </h1>
                                <p className="text-sm" style={{ color: '#666' }}>
                                    System Zarządzania Rekrutacją
                                </p>
                            </div>
                            <img src="./src/assets/bobr.webp" alt="bober" className="img-fixed"></img>
                        </div>
                    </div>

                    <div className="flex items-center justify-end gap-2">
                        <img src="./src/assets/bobr.gif" alt="bober" className="img-fixed"></img>
                        <img src="./src/assets/bobr.gif" alt="bober" className="img-fixed"></img>
                        <img src="./src/assets/bobr.gif" alt="bober" className="img-fixed"></img>
                        <img src="./src/assets/bobr.gif" alt="bober" className="img-fixed"></img>
                        <img src="./src/assets/bobr.gif" alt="bober" className="img-fixed"></img>
                    </div>
                </div>
            </div>
        </header>
    )
}
