import { Button, Modal } from 'antd'
import React, { ReactElement, useState } from 'react'
import './Room.css'

export default function Room({
    roomName,
    peopleInRoom
}: {
    roomName: string
    peopleInRoom: string[]
}): ReactElement {
    const [modalVisible, setModalVisible] = useState<boolean>(false)

    const onModalOk = () => {
        // Add logic for starting python stuff
    }

    const createPeopleInRoomElement = (): ReactElement => {
        return peopleInRoom.length === 0 ? <div className='people-in-room'><p>Room is empty</p></div> : (
            <div className='people-in-room'>
                {peopleInRoom.map((value, i) => <p key={i}>{value}</p>)}
            </div>
        );
    }

    return (
        <div className='room-container'>
            <h2>{roomName}</h2>
            <div>
                {createPeopleInRoomElement()}
                <Button type='primary' onClick={() => setModalVisible(true)}>
                    Join {roomName} room
                </Button>
                <Modal
                    title={"Join " + roomName + "?"} 
                    visible={modalVisible}
                    onOk={onModalOk}
                    onCancel={() => setModalVisible(false)}
                >
                    <p>Do you want to join the {roomName.toLowerCase()} room?</p>
                </Modal>
            </div>
        </div>
    )
}