type ShipType = {
    ship_id: string,
    ship_name: string
}

type GetShipsResponse = {
    latitude: number,
    longitude: number,
    ship_id: number,
    ship_name: string
}

export type {ShipType, GetShipsResponse}