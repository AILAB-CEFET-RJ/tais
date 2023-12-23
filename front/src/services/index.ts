import axios from "axios"

const aisAPI = axios.create({
    baseURL: process.env.REACT_APP_HOST_API_URL
})

export { aisAPI }