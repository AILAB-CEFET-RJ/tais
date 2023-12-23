import { Box, Typography } from "@mui/material"
import DirectionsBoatFilledTwoToneIcon from '@mui/icons-material/DirectionsBoatFilledTwoTone';


const Header: React.FC = () => {
    return <Box
        width='100%'
        height='60px'
        bgcolor='#55586610'
        display='flex'
        alignItems='center'
        justifyContent='flex-start'
        padding='16px 24px'
        gap={'8px'}
        color={'#555866'}
        fontWeight={700}
        borderBottom={'1px solid #55586650'}
        >   
            <DirectionsBoatFilledTwoToneIcon />
            <Typography
            variant="h1"
            fontSize={'24px'}
            fontFamily={'Poppins'}
            >TaisApp</Typography>
    </Box>
}

export default Header