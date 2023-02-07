-- CreateTable
CREATE TABLE "_InventoryItemRolesToAdd" (
    "A" INTEGER NOT NULL,
    "B" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "_InventoryItemRolesToRemove" (
    "A" INTEGER NOT NULL,
    "B" TEXT NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "_InventoryItemRolesToAdd_AB_unique" ON "_InventoryItemRolesToAdd"("A", "B");

-- CreateIndex
CREATE INDEX "_InventoryItemRolesToAdd_B_index" ON "_InventoryItemRolesToAdd"("B");

-- CreateIndex
CREATE UNIQUE INDEX "_InventoryItemRolesToRemove_AB_unique" ON "_InventoryItemRolesToRemove"("A", "B");

-- CreateIndex
CREATE INDEX "_InventoryItemRolesToRemove_B_index" ON "_InventoryItemRolesToRemove"("B");

-- AddForeignKey
ALTER TABLE "_InventoryItemRolesToAdd" ADD CONSTRAINT "_InventoryItemRolesToAdd_A_fkey" FOREIGN KEY ("A") REFERENCES "InventoryItem"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_InventoryItemRolesToAdd" ADD CONSTRAINT "_InventoryItemRolesToAdd_B_fkey" FOREIGN KEY ("B") REFERENCES "Role"("snowflake") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_InventoryItemRolesToRemove" ADD CONSTRAINT "_InventoryItemRolesToRemove_A_fkey" FOREIGN KEY ("A") REFERENCES "InventoryItem"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_InventoryItemRolesToRemove" ADD CONSTRAINT "_InventoryItemRolesToRemove_B_fkey" FOREIGN KEY ("B") REFERENCES "Role"("snowflake") ON DELETE CASCADE ON UPDATE CASCADE;
