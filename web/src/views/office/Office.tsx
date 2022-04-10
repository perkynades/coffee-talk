import React, { ReactElement, useState } from 'react'
import { useLocation } from 'react-router-dom'
import Room from '../../components/Room'
import './Office.css'

interface IPeopleInRoom {
    peopleInRoom: string[]
}

export default function Office(): ReactElement {
    const { state }: {state: any} = useLocation()
    
    const [peopleInRooms, setPeopleInRooms] = useState<IPeopleInRoom>()

    const populatePeopleInRooms = () => {
        // Add communication with mqtt broker?
    }

    return (
        <div>
            <h1 className='office-info'>Sales AS, Oslovegen 1</h1>
            <div className='rooms-container'>
                <Room roomName='Cantine' peopleInRoom={["Emil", "Sebastian"]}/>
                <Room roomName='Coffee' peopleInRoom={["Hanne"]}/>
                <Room roomName='Ping-pong' peopleInRoom={["Jonatan", "Emilie"]}/>
                <Room roomName='Lounge' peopleInRoom={[]}/>
            </div>
        </div>
    )
}