import axios from "axios"

const aisAPI = axios.create({
    baseURL: "http://localhost:3001"
})

export { aisAPI }