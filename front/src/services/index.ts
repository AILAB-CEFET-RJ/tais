import axios from "axios"

const aisAPI = axios.create({
    baseURL: process.env.REACT_APP_API_URL || "http://localhost:5000"
})

export { aisAPI }