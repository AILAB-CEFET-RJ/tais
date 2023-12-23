import styled from "@emotion/styled";
import { FilledTextFieldProps, TextField } from "@mui/material";


const CordTextField = styled(TextField)`
    background-color: #fff;
    border-radius: 8px;
    outline: none;
    font-family: 'Poppins', sans-serif;

    & .MuiFilledInput-input, .MuiInputLabel-root{
        font-family: 'Poppins', sans-serif;
        font-size: 16px;
    }


    & .MuiFilledInput-root{
        background-color: transparent;
    }

    & .MuiFilledInput-root:hover{
        background-color: transparent;
        border: none;
    }

    & .MuiFilledInput-root:before, .MuiFilledInput-root:after, {
        border: none;
    }

    & .MuiFilledInput-root:hover:before{
        border: none !important;
    }

    & .MuiFilledInput-root:hover:after{
        border: none;
    }

    & .MuiFilledInput-root.Mui-focused{
        background-color: transparent;

    }

`

export {CordTextField}