import axios from "axios"

const aisAPI = axios.create({
    baseURL: "http://localhost:5000"
})

export { aisAPI }