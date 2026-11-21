/* XIAO nRF52840 with the stock Adafruit UF2 bootloader kept intact (bootloader lives at the top of flash).
   Application starts at 0x27000 -- ASSUMED from forum reports; VERIFY against the bootloader before flashing. No SoftDevice region is used
   (BLE would come from nrf-sdc linked into the app), but 0x27000 keeps UF2 drag-and-drop compatible. */
MEMORY
{
  FLASH : ORIGIN = 0x00027000, LENGTH = 0x000CD000
  RAM   : ORIGIN = 0x20000008, LENGTH = 0x0003FFF8
}
