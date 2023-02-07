-- CreateTable
CREATE TABLE "_ItemRolesRequired" (
    "A" INTEGER NOT NULL,
    "B" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "_ItemRolesToAdd" (
    "A" INTEGER NOT NULL,
    "B" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "_ItemRolesToRemove" (
    "A" INTEGER NOT NULL,
    "B" TEXT NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "_ItemRolesRequired_AB_unique" ON "_ItemRolesRequired"("A", "B");

-- CreateIndex
CREATE INDEX "_ItemRolesRequired_B_index" ON "_ItemRolesRequired"("B");

-- CreateIndex
CREATE UNIQUE INDEX "_ItemRolesToAdd_AB_unique" ON "_ItemRolesToAdd"("A", "B");

-- CreateIndex
CREATE INDEX "_ItemRolesToAdd_B_index" ON "_ItemRolesToAdd"("B");

-- CreateIndex
CREATE UNIQUE INDEX "_ItemRolesToRemove_AB_unique" ON "_ItemRolesToRemove"("A", "B");

-- CreateIndex
CREATE INDEX "_ItemRolesToRemove_B_index" ON "_ItemRolesToRemove"("B");

-- AddForeignKey
ALTER TABLE "_ItemRolesRequired" ADD CONSTRAINT "_ItemRolesRequired_A_fkey" FOREIGN KEY ("A") REFERENCES "Item"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_ItemRolesRequired" ADD CONSTRAINT "_ItemRolesRequired_B_fkey" FOREIGN KEY ("B") REFERENCES "Role"("snowflake") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_ItemRolesToAdd" ADD CONSTRAINT "_ItemRolesToAdd_A_fkey" FOREIGN KEY ("A") REFERENCES "Item"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_ItemRolesToAdd" ADD CONSTRAINT "_ItemRolesToAdd_B_fkey" FOREIGN KEY ("B") REFERENCES "Role"("snowflake") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_ItemRolesToRemove" ADD CONSTRAINT "_ItemRolesToRemove_A_fkey" FOREIGN KEY ("A") REFERENCES "Item"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_ItemRolesToRemove" ADD CONSTRAINT "_ItemRolesToRemove_B_fkey" FOREIGN KEY ("B") REFERENCES "Role"("snowflake") ON DELETE CASCADE ON UPDATE CASCADE;
